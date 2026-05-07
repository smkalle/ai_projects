"""FastAPI backend for Iteration 1."""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai.errors import APIError
from pydantic import BaseModel

from backend.pipeline import (
    _routing_decision,
    _validate_fields,
    get_default_model,
    run_classify,
    run_coverage,
    run_extract,
    run_fraud_signals,
)
from backend.rag_store import InMemoryRagStore

# Load .env from project root (two levels up from this file)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_PROJECT_ROOT / ".env")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Insurance Claims Workflow", version="0.1.0")
RAG_STORE = InMemoryRagStore()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _get_genai_client() -> genai.Client:
    """Factory for the Gemini client (patchable in tests)."""
    key = os.environ.get("GOOGLE_API_KEY", "").strip() or os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        raise RuntimeError("Set GOOGLE_API_KEY (or GEMINI_API_KEY) in .env or environment.")
    return genai.Client(api_key=key)


class ClaimsRequest(BaseModel):
    prompt: str
    model: str | None = None


class HealthResponse(BaseModel):
    status: str
    gemini: bool


class ClaimsResponse(BaseModel):
    claim: dict[str, Any]
    classification: dict[str, Any]
    coverage: dict[str, Any]
    fraud_signals: dict[str, Any]
    validation: dict[str, Any]
    routing: dict[str, Any]
    citations: list[dict[str, Any]]
    attachment_insights: dict[str, Any]
    trace: list[dict[str, Any]] | None = None


class SourceIngestRequest(BaseModel):
    text: str | None = None
    url: str | None = None
    title: str | None = None


class SourceIngestResponse(BaseModel):
    source_id: str
    title: str
    source_type: str
    mime_type: str | None = None
    kind: str | None = None
    processing: dict[str, Any] | None = None
    vision_findings: dict[str, Any] | None = None
    total_sources: int


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Health check confirming basic availability."""
    return HealthResponse(status="ok", gemini=True)


@app.post("/claims", response_model=ClaimsResponse)
async def claims(req: ClaimsRequest) -> ClaimsResponse:
    """Run Steps 1 (Extract), 2 (Classify), 3 (Validate), 6 (Route partial)."""
    client = _get_genai_client()
    model = req.model or get_default_model()
    debug = os.environ.get("DEBUG", "1") == "1"
    trace: list[dict[str, Any]] = []

    logger.info("Running claim pipeline for model=%s", model)

    try:
        # Step 1: Extract
        t0 = __import__("time").time()
        claim = run_extract(client, req.prompt, model)
        trace.append({
            "step": 1,
            "name": "Extract",
            "input": req.prompt,
            "output": claim,
            "duration_ms": round((__import__("time").time() - t0) * 1000, 2),
        })

        # Step 2: Classify
        t0 = __import__("time").time()
        classification = run_classify(client, claim, model)
        trace.append({
            "step": 2,
            "name": "Classify",
            "input": claim,
            "output": classification,
            "duration_ms": round((__import__("time").time() - t0) * 1000, 2),
        })

        # Step 3: Validate (deterministic)
        validation = _validate_fields(claim)
        trace.append({
            "step": 3,
            "name": "Validate",
            "input": claim,
            "output": validation,
            "duration_ms": 0,
        })

        # Step 4 retrieval: single pass per /claims call
        t0 = __import__("time").time()
        retrieval_results = RAG_STORE.retrieve(req.prompt, top_k=3)
        citations = [
            {
                "source_id": item["source_id"],
                "title": item["title"],
                "snippet": item["snippet"],
                "score": item["score"],
            }
            for item in retrieval_results
        ]
        policy_context = "\n\n".join(item["content"] for item in retrieval_results) if retrieval_results else None
        trace.append({
            "step": 4,
            "name": "RetrievePolicyEvidence",
            "input": req.prompt,
            "output": {"retrieved": len(retrieval_results), "citations": citations},
            "duration_ms": round((__import__("time").time() - t0) * 1000, 2),
        })

        # Step 4: Coverage (LLM, grounded by retrieval when available)
        t0 = __import__("time").time()
        coverage = run_coverage(client, claim, classification, policy_context=policy_context, model=model)
        trace.append({
            "step": 4,
            "name": "Coverage",
            "input": {"claim": claim, "classification": classification, "policy_grounded": bool(policy_context)},
            "output": coverage,
            "duration_ms": round((__import__("time").time() - t0) * 1000, 2),
        })

        # Step 5: Fraud signals
        t0 = __import__("time").time()
        fraud_signals = run_fraud_signals(client, claim, model)
        trace.append({
            "step": 5,
            "name": "FraudSignals",
            "input": claim,
            "output": fraud_signals,
            "duration_ms": round((__import__("time").time() - t0) * 1000, 2),
        })

        # Step 6: Route (deterministic, full with fraud/safety)
        routing = _routing_decision(validation, classification, fraud_signals)
        trace.append({
            "step": 6,
            "name": "Route",
            "input": {"validation": validation, "classification": classification, "fraud_signals": fraud_signals},
            "output": routing,
            "duration_ms": 0,
        })

        attachment_insights = _build_attachment_insights(retrieval_results)

        return ClaimsResponse(
            claim=claim,
            classification=classification,
            coverage=coverage,
            fraud_signals=fraud_signals,
            validation=validation,
            routing=routing,
            citations=citations,
            attachment_insights=attachment_insights,
            trace=trace if debug else None,
        )
    except APIError as exc:
        detail: dict[str, Any] = {
            "message": str(exc),
            "provider_error": True,
            "trace": trace if debug else None,
        }
        status_code = getattr(exc, "status_code", None)
        if isinstance(status_code, int):
            detail["status_code"] = status_code
            if status_code in (429, 503):
                raise HTTPException(status_code=503, detail=detail) from exc
        raise HTTPException(status_code=502, detail=detail) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={"message": str(exc), "trace": trace if debug else None},
        ) from exc


@app.post("/sources", response_model=SourceIngestResponse)
async def sources(request: Request) -> SourceIngestResponse:
    """Ingest source text or URL into in-memory retrieval store."""
    allow_private = os.environ.get("ALLOW_PRIVATE_URLS", "false").lower() == "true"
    content_type = request.headers.get("content-type", "")

    if content_type.startswith("multipart/form-data"):
        form = await request.form()
        upload = form.get("file")
        title = form.get("title")
        kind = str(form.get("kind") or "other")
        if upload is None:
            raise HTTPException(status_code=400, detail="Missing file in multipart form.")
        file_bytes = await upload.read()
        try:
            needs_llm = (upload.content_type or "").startswith("image/")
            result = RAG_STORE.add_file(
                file_bytes,
                filename=upload.filename or "upload.bin",
                mime_type=upload.content_type or "application/octet-stream",
                kind=kind,
                client=_get_genai_client() if needs_llm else None,
                model=get_default_model() if needs_llm else None,
            )
            if title:
                result["title"] = str(title)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    else:
        payload = SourceIngestRequest(**(await request.json()))
        if payload.text and payload.text.strip():
            result = RAG_STORE.add_text(payload.text, title=payload.title)
        elif payload.url and payload.url.strip():
            try:
                result = RAG_STORE.add_url(payload.url.strip(), allow_private=allow_private)
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc
        else:
            raise HTTPException(status_code=400, detail="Provide either text or url in /sources payload")

    return SourceIngestResponse(
        source_id=result["source_id"],
        title=result["title"],
        source_type=result["source_type"],
        mime_type=result.get("mime_type"),
        kind=result.get("kind"),
        processing=result.get("processing"),
        vision_findings=result.get("vision_findings"),
        total_sources=RAG_STORE.count(),
    )


def _build_attachment_insights(retrieval_results: list[dict[str, Any]]) -> dict[str, Any]:
    damage_findings: list[dict[str, Any]] = []
    recommended_next_evidence: list[str] = []
    document_highlights: list[str] = []
    drivable_risk = "unknown"

    for item in retrieval_results:
        vision = item.get("vision_findings")
        if vision:
            damage_findings.extend(vision.get("damage_findings") or [])
            recommended_next_evidence.extend(vision.get("recommended_next_evidence") or [])
            drivable_risk = vision.get("drivable_risk") or drivable_risk
        if item.get("source_type") in {"text", "url", "file"} and item.get("snippet"):
            document_highlights.append(item["snippet"])

    # de-duplicate while preserving order
    seen = set()
    dedup_reco = []
    for rec in recommended_next_evidence:
        if rec not in seen:
            seen.add(rec)
            dedup_reco.append(rec)

    return {
        "damage_findings": damage_findings,
        "drivable_risk": drivable_risk,
        "recommended_next_evidence": dedup_reco,
        "document_highlights": document_highlights[:3],
    }
