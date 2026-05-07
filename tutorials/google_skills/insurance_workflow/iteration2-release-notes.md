# Iteration 2 Release Notes

Date: 2026-05-07

## Release Summary

Iteration 2 adds coverage reasoning and a production-style React intake UI while preserving Iteration 1 claim extraction/classification/routing behavior.

## Highlights

- Added Step 4 Coverage decision using static policy context in `backend/pipeline.py`.
- Extended `/claims` response with a `coverage` object in `backend/server.py`.
- Replaced static HTML frontend with React + Vite app in `frontend/`.
- Added UI sections for Claim Facts, Classification, Coverage, Routing, Missing Fields, and Debug Trace.
- Added model fallback chain from `.env`:
  - `GEMINI_FALLBACK_MODELS=gemini-3.1-flash-lite-preview,gemini-2.5-flash-lite,gemini-2.5-flash`
- Added stronger deterministic validation:
  - required field presence
  - basic incident date sanity check (invalid calendar dates flagged)

## API Contract Changes

`POST /claims` now includes:

```json
{
  "coverage": {
    "is_covered": true,
    "coverage_rationale": "...",
    "deductible_applicable": "$500 per covered collision loss"
  },
  "validation": {
    "has_all_fields": true,
    "missing_fields": [],
    "has_valid_fields": true,
    "invalid_fields": []
  }
}
```

Backward-compatible fields from Iteration 1 remain present.

## Frontend

- New React app served on `http://localhost:5177`.
- `run.sh` updated to run backend + frontend debug workflow.

## Quality / Verification

- Unit/non-integration tests pass locally.
- Integration tests are currently blocked intermittently by Gemini free-tier quota (`429 RESOURCE_EXHAUSTED`).

## Known Issues

- External integration calls may fail under quota limits despite retry/fallback logic.
- Claims Ops manual sign-off still required for rationale quality on real examples.

## Upgrade Notes

- Ensure `.env` includes:
  - `GEMINI_MODEL`
  - `GEMINI_FALLBACK_MODELS`
  - `GOOGLE_API_KEY` or `GEMINI_API_KEY`
- Start with:

```bash
./run.sh
```
