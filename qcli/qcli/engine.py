from __future__ import annotations

from dataclasses import dataclass
from threading import Thread
from typing import Iterable

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer


@dataclass
class EngineOptions:
    model_id: str
    device: str = "auto"
    dtype: str = "auto"
    quantized: str = "none"
    trust_remote_code: bool = False


class LocalHFEngine:
    def __init__(self, options: EngineOptions) -> None:
        self.options = options
        self.device = self._resolve_device(options.device)
        self.dtype = self._resolve_dtype(options.dtype)
        self.tokenizer = AutoTokenizer.from_pretrained(
            options.model_id,
            trust_remote_code=options.trust_remote_code,
        )
        self.model = self._load_model()
        self.input_device = self._resolve_input_device()

    def _resolve_device(self, requested: str) -> str:
        if requested != "auto":
            return requested
        if torch.cuda.is_available():
            return "cuda"
        if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
            return "mps"
        return "cpu"

    def _resolve_dtype(self, requested: str) -> torch.dtype:
        if requested == "float16":
            return torch.float16
        if requested == "bfloat16":
            return torch.bfloat16
        if requested == "float32":
            return torch.float32
        if self.device == "cuda":
            return torch.float16
        return torch.float32

    def _load_model(self) -> AutoModelForCausalLM:
        kwargs = {
            "trust_remote_code": self.options.trust_remote_code,
        }
        if self.options.quantized == "none":
            kwargs["torch_dtype"] = self.dtype
            return AutoModelForCausalLM.from_pretrained(
                self.options.model_id,
                **kwargs,
            ).to(self.device)

        if self.device != "cuda":
            raise RuntimeError("Quantized loading requires CUDA. Use --device cuda or --quantized none.")

        try:
            from transformers import BitsAndBytesConfig
        except ImportError as exc:  # pragma: no cover - depends on optional package
            raise RuntimeError(
                "bitsandbytes support is missing. Install extras: pip install -e '.[quant]'"
            ) from exc

        if self.options.quantized == "4bit":
            kwargs["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=self.dtype,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
            )
        elif self.options.quantized == "8bit":
            kwargs["quantization_config"] = BitsAndBytesConfig(load_in_8bit=True)
        else:
            raise ValueError(f"Unsupported quantized mode: {self.options.quantized}")

        kwargs["device_map"] = "auto"
        return AutoModelForCausalLM.from_pretrained(self.options.model_id, **kwargs)

    def _resolve_input_device(self) -> torch.device:
        try:
            return next(self.model.parameters()).device
        except StopIteration:  # pragma: no cover - defensive
            return torch.device(self.device)

    def _build_prompt(self, messages: list[dict[str, str]]) -> str:
        if hasattr(self.tokenizer, "apply_chat_template"):
            return self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )
        merged = []
        for item in messages:
            merged.append(f"{item['role']}: {item['content']}")
        merged.append("assistant:")
        return "\n".join(merged)

    def generate_stream(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float,
        top_p: float,
        max_new_tokens: int,
    ) -> Iterable[str]:
        prompt = self._build_prompt(messages)
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.input_device)
        streamer = TextIteratorStreamer(
            self.tokenizer,
            skip_prompt=True,
            skip_special_tokens=True,
        )
        kwargs = {
            **inputs,
            "streamer": streamer,
            "max_new_tokens": max_new_tokens,
            "do_sample": temperature > 0,
            "temperature": max(temperature, 1e-5),
            "top_p": top_p,
            "pad_token_id": self.tokenizer.eos_token_id,
            "eos_token_id": self.tokenizer.eos_token_id,
        }

        gen_error: BaseException | None = None

        def _generate() -> None:
            nonlocal gen_error
            try:
                self.model.generate(**kwargs)
            except BaseException as exc:
                gen_error = exc
                streamer.end()

        worker = Thread(target=_generate)
        worker.start()
        for chunk in streamer:
            yield chunk
        worker.join()
        if gen_error is not None:
            raise gen_error

    def generate_text(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float,
        top_p: float,
        max_new_tokens: int,
    ) -> str:
        return "".join(
            self.generate_stream(
                messages,
                temperature=temperature,
                top_p=top_p,
                max_new_tokens=max_new_tokens,
            )
        )
