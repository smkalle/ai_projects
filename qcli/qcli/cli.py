from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from qcli.engine import EngineOptions, LocalHFEngine
from qcli.session import ChatSession, parse_command

console = Console()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="qcli: local terminal chat for Hugging Face models")
    parser.add_argument("--model", default="Qwen/Qwen3.5-2B", help="Hugging Face model ID")
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--top-p", type=float, default=0.9)
    parser.add_argument("--max-new-tokens", type=int, default=512)
    parser.add_argument("--system", default="You are a helpful assistant.")
    parser.add_argument("--device", default="auto", help="auto|cpu|cuda|mps")
    parser.add_argument("--dtype", default="auto", help="auto|float16|bfloat16|float32")
    parser.add_argument("--quantized", default="none", choices=["none", "4bit", "8bit"])
    parser.add_argument("--trust-remote-code", action="store_true")
    parser.add_argument("--history-file", default=None, help="optional session JSON file to load at start")
    parser.add_argument("--no-stream", action="store_true", help="disable token streaming")
    return parser


def _help_text() -> str:
    return (
        "Commands:\n"
        "/help\n"
        "/clear\n"
        "/save <path>\n"
        "/load <path>\n"
        "/system <text>\n"
        "/set temperature <float>\n"
        "/set top_p <float>\n"
        "/set max_new_tokens <int>\n"
        "/exit"
    )


def _apply_set(session: ChatSession, key: str, value: str) -> str:
    if key == "temperature":
        session.config.temperature = float(value)
        return f"temperature={session.config.temperature}"
    if key == "top_p":
        session.config.top_p = float(value)
        return f"top_p={session.config.top_p}"
    if key == "max_new_tokens":
        session.config.max_new_tokens = int(value)
        return f"max_new_tokens={session.config.max_new_tokens}"
    raise ValueError("unknown key")


def _handle_command(session: ChatSession, command: str, args: list[str]) -> bool:
    if command in {"exit", "quit"}:
        return True
    if command == "help":
        console.print(Panel(_help_text(), title="qcli"))
        return False
    if command == "clear":
        session.reset()
        console.print("[cyan]History cleared.[/cyan]")
        return False
    if command == "save":
        if not args:
            console.print("[red]Usage: /save <path>[/red]")
            return False
        session.save(args[0])
        console.print(f"[green]Saved:[/green] {args[0]}")
        return False
    if command == "load":
        if not args:
            console.print("[red]Usage: /load <path>[/red]")
            return False
        loaded = ChatSession.load(args[0])
        session.system_prompt = loaded.system_prompt
        session.config = loaded.config
        session.messages = loaded.messages
        console.print(f"[green]Loaded:[/green] {args[0]}")
        return False
    if command == "system":
        if not args:
            console.print("[red]Usage: /system <text>[/red]")
            return False
        session.set_system_prompt(" ".join(args))
        console.print("[green]System prompt updated.[/green]")
        return False
    if command == "set":
        if len(args) != 2:
            console.print("[red]Usage: /set <temperature|top_p|max_new_tokens> <value>[/red]")
            return False
        try:
            result = _apply_set(session, args[0], args[1])
            console.print(f"[green]Updated:[/green] {result}")
        except Exception as exc:  # noqa: BLE001
            console.print(f"[red]Failed to update setting:[/red] {exc}")
        return False

    console.print(f"[red]Unknown command:[/red] /{command}")
    return False


def run_chat(args: argparse.Namespace) -> int:
    session = ChatSession(
        system_prompt=args.system,
    )
    session.config.temperature = args.temperature
    session.config.top_p = args.top_p
    session.config.max_new_tokens = args.max_new_tokens

    if args.history_file and Path(args.history_file).exists():
        session = ChatSession.load(args.history_file)

    engine = LocalHFEngine(
        EngineOptions(
            model_id=args.model,
            device=args.device,
            dtype=args.dtype,
            quantized=args.quantized,
            trust_remote_code=args.trust_remote_code,
        )
    )

    console.print(Panel("qcli is ready. Type /help for commands.", title="qcli"))

    while True:
        try:
            line = console.input("[bold cyan]you> [/bold cyan]").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Exiting...[/yellow]")
            break

        if not line:
            continue

        parsed = parse_command(line)
        if parsed:
            cmd, argv = parsed
            should_exit = _handle_command(session, cmd, argv)
            if should_exit:
                break
            continue

        session.add_user(line)
        console.print("[bold green]assistant>[/bold green] ", end="")
        try:
            if args.no_stream:
                response = engine.generate_text(
                    session.messages,
                    temperature=session.config.temperature,
                    top_p=session.config.top_p,
                    max_new_tokens=session.config.max_new_tokens,
                )
                console.print(response)
            else:
                pieces: list[str] = []
                for chunk in engine.generate_stream(
                    session.messages,
                    temperature=session.config.temperature,
                    top_p=session.config.top_p,
                    max_new_tokens=session.config.max_new_tokens,
                ):
                    pieces.append(chunk)
                    console.print(chunk, end="")
                console.print()
                response = "".join(pieces)
        except Exception as exc:  # noqa: BLE001
            console.print()
            console.print(f"[red]Generation failed:[/red] {exc}")
            session.messages.pop()  # remove orphaned user message
            continue

        session.add_assistant(response)

    if args.history_file:
        session.save(args.history_file)
        console.print(f"[green]Session saved:[/green] {args.history_file}")

    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return run_chat(args)


if __name__ == "__main__":
    raise SystemExit(main())
