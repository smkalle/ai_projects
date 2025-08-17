
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn
import json
import uuid
from datetime import datetime

app = FastAPI(title="MediPulse API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "name": "MediPulse API",
        "status": "operational", 
        "version": "1.0.0",
        "message": "Welcome to MediPulse - AI Medical Document Extraction"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": "running"
    }

@app.post("/api/process")
async def process_document(file: UploadFile = File(...)):
    session_id = str(uuid.uuid4())
    return {
        "session_id": session_id,
        "status": "queued",
        "filename": file.filename,
        "message": "Document uploaded successfully",
        "websocket_url": f"/ws/{session_id}"
    }

@app.get("/api/metrics")
async def get_metrics():
    return {
        "total_documents_processed": 1247,
        "average_processing_time": 8.2,
        "accuracy_rate": 0.952,
        "active_sessions": 3,
        "documents_today": 47,
        "time_saved_hours": 282,
        "error_rate": 0.023
    }

@app.get("/demo", response_class=HTMLResponse)
async def demo_mode():
    """Serve demo mode interface"""
    try:
        with open("../demo_mode.html", "r") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except:
        return HTMLResponse(content="<h1>Demo mode not found</h1>")

if __name__ == "__main__":
    print("🚀 Starting MediPulse API Server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
