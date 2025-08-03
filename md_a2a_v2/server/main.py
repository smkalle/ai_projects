from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict
from graph import app as lg_app

app = FastAPI(title="Multiagent A2A API", version="0.1.0")

# Allow Streamlit (localhost) and simple demos. Tighten in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}

@app.post("/query")
def query(req: QueryRequest) -> Dict[str, Any]:
    state = {"messages": [{"role": "user", "content": req.query}]}
    result = lg_app.invoke(state)
    # result may be a dict, Command, or message-like object; stringify if needed
    try:
        return {"ok": True, "data": result}
    except Exception:
        return {"ok": True, "data": str(result)}
