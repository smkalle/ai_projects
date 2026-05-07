"""Simple in-memory source store and retrieval for Iteration 3."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen
import re

from google import genai
from google.genai import types


@dataclass
class SourceRecord:
    source_id: str
    source_type: str
    content: str
    title: str
    created_at: str
    mime_type: str | None = None
    filename: str | None = None
    kind: str | None = None
    vision_findings: dict[str, Any] | None = None


class InMemoryRagStore:
    def __init__(self) -> None:
        self._sources: list[SourceRecord] = []

    def _add_record(self, record: SourceRecord) -> dict[str, Any]:
        self._sources.append(record)
        return {
            "source_id": record.source_id,
            "title": record.title,
            "source_type": record.source_type,
            "mime_type": record.mime_type,
            "kind": record.kind,
            "vision_findings": record.vision_findings,
            "processing": {
                "text_extracted": bool(record.content),
                "vision_analyzed": record.vision_findings is not None,
            },
        }

    def add_text(self, text: str, title: str | None = None) -> dict[str, Any]:
        source_id = f"src_{len(self._sources) + 1:04d}"
        record = SourceRecord(
            source_id=source_id,
            source_type="text",
            content=text.strip(),
            title=title or f"Source {source_id}",
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        return self._add_record(record)

    def add_url(self, url: str, allow_private: bool = False) -> dict[str, Any]:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        if not allow_private and host in {"localhost", "127.0.0.1", "0.0.0.0"}:
            raise ValueError("Private/localhost URLs blocked. Set ALLOW_PRIVATE_URLS=true for local dev.")
        req = Request(url, headers={"User-Agent": "insurance-workflow/1.0"})
        with urlopen(req, timeout=20) as response:  # nosec B310
            body = response.read().decode("utf-8", errors="replace")
        title = parsed.netloc or url
        return self.add_text(body, title=title)

    def add_file(
        self,
        file_bytes: bytes,
        *,
        filename: str,
        mime_type: str,
        kind: str,
        client: genai.Client | None = None,
        model: str | None = None,
        max_bytes: int = 15 * 1024 * 1024,
    ) -> dict[str, Any]:
        if len(file_bytes) == 0:
            raise ValueError("Uploaded file is empty.")
        if len(file_bytes) > max_bytes:
            raise ValueError("File exceeds 15MB limit.")

        supported = {
            "image/jpeg",
            "image/png",
            "image/webp",
            "application/pdf",
            "text/plain",
            "text/markdown",
        }
        if mime_type not in supported:
            raise ValueError(f"Unsupported file type: {mime_type}")

        source_id = f"src_{len(self._sources) + 1:04d}"
        title = filename or f"Source {source_id}"
        content = ""
        vision_findings = None

        if mime_type.startswith("text/"):
            content = file_bytes.decode("utf-8", errors="replace").strip()
        elif mime_type.startswith("image/"):
            if client is None or not model:
                raise ValueError("Image analysis requires configured Gemini client and model.")
            vision_findings = _analyze_image_with_gemini(client, model, file_bytes, mime_type)
            content = _vision_summary_text(vision_findings)
        elif mime_type == "application/pdf":
            content = f"PDF document uploaded: {title}."

        record = SourceRecord(
            source_id=source_id,
            source_type="file",
            content=content,
            title=title,
            created_at=datetime.now(timezone.utc).isoformat(),
            mime_type=mime_type,
            filename=filename,
            kind=kind,
            vision_findings=vision_findings,
        )
        return self._add_record(record)

    def retrieve(self, query: str, top_k: int = 3) -> list[dict[str, Any]]:
        if not self._sources:
            return []
        query_terms = _tokenize(query)
        scored: list[tuple[int, SourceRecord]] = []
        for src in self._sources:
            source_terms = _tokenize(src.content)
            overlap = len(query_terms & source_terms)
            scored.append((overlap, src))
        scored.sort(key=lambda x: x[0], reverse=True)
        results = []
        for score, src in scored[:top_k]:
            snippet = src.content[:350].replace("\n", " ")
            results.append(
                {
                    "source_id": src.source_id,
                    "title": src.title,
                    "source_type": src.source_type,
                    "score": score,
                    "snippet": snippet,
                    "content": src.content,
                    "mime_type": src.mime_type,
                    "filename": src.filename,
                    "kind": src.kind,
                    "vision_findings": src.vision_findings,
                }
            )
        return results

    def count(self) -> int:
        return len(self._sources)


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", (text or "").lower()))


def _analyze_image_with_gemini(client: genai.Client, model: str, data: bytes, mime_type: str) -> dict[str, Any]:
    schema = {
        "type": "object",
        "properties": {
            "damage_findings": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "part": {"type": "string"},
                        "severity": {"type": "string"},
                        "confidence_note": {"type": "string"},
                    },
                    "required": ["part", "severity", "confidence_note"],
                },
            },
            "drivable_risk": {"type": "string"},
            "recommended_next_evidence": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["damage_findings", "drivable_risk", "recommended_next_evidence"],
    }
    response = client.models.generate_content(
        model=model,
        contents=[
            "Analyze visible vehicle damage only. Return concise JSON and avoid assumptions beyond visible evidence.",
            types.Part.from_bytes(data=data, mime_type=mime_type),
        ],
        config=types.GenerateContentConfig(responseMimeType="application/json", responseSchema=schema),
    )
    parsed = getattr(response, "parsed", None)
    if isinstance(parsed, dict):
        return parsed
    if parsed is not None and hasattr(parsed, "model_dump"):
        return parsed.model_dump()
    return {"damage_findings": [], "drivable_risk": "unknown", "recommended_next_evidence": []}


def _vision_summary_text(vision: dict[str, Any] | None) -> str:
    if not vision:
        return "Image uploaded with no structured findings."
    findings = vision.get("damage_findings") or []
    parts = ", ".join(item.get("part", "unknown") for item in findings[:4])
    risk = vision.get("drivable_risk", "unknown")
    return f"Image findings: parts={parts or 'none'}, drivable_risk={risk}."
