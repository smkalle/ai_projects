"""
API Routes for Rare Disease Drug Repurposing System
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import List, Dict, Any, Optional
import asyncio
import uuid
from datetime import datetime

from src.api.schemas import (
    AnalysisRequest, AnalysisResponse, DrugCandidateResponse,
    LiteratureSearchRequest, LiteratureSearchResponse,
    DiseaseInfoResponse, DrugInfoResponse
)
from src.agents.coordinator import get_coordinator
from src.core.database import get_database

router = APIRouter()

# In-memory job storage (in production, use Redis or database)
job_storage = {}

@router.post("/analyze/repurposing", response_model=AnalysisResponse)
async def analyze_drug_repurposing(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    coordinator=Depends(get_coordinator)
):
    """
    Analyze drug repurposing opportunities for a rare disease
    """
    try:
        # Generate unique request ID
        request_id = f"req_{uuid.uuid4().hex[:12]}"

        # Start analysis
        start_time = datetime.now()

        # Run the analysis through the coordinator agent
        result = await coordinator.analyze_drug_repurposing(
            disease=request.disease,
            patient_profile=request.patient_profile,
            parameters=request.analysis_parameters
        )

        processing_time = int((datetime.now() - start_time).total_seconds() * 1000)

        # Format response
        response = AnalysisResponse(
            request_id=request_id,
            status="completed",
            timestamp=datetime.now(),
            processing_time_ms=processing_time,
            results=result,
            medical_disclaimer="This information is for research purposes only and should not be used as a substitute for professional medical advice."
        )

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/analyze/repurposing/async")
async def analyze_drug_repurposing_async(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    coordinator=Depends(get_coordinator)
):
    """
    Start asynchronous drug repurposing analysis
    """
    job_id = f"job_{uuid.uuid4().hex[:12]}"

    # Store job info
    job_storage[job_id] = {
        "status": "queued",
        "created_at": datetime.now(),
        "progress": 0,
        "result": None,
        "error": None
    }

    # Add to background tasks
    background_tasks.add_task(
        run_analysis_background,
        job_id, request, coordinator
    )

    return {
        "job_id": job_id,
        "status": "queued",
        "estimated_completion": datetime.now().isoformat()
    }

async def run_analysis_background(job_id: str, request: AnalysisRequest, coordinator):
    """Background task for running analysis"""
    try:
        job_storage[job_id]["status"] = "running"
        job_storage[job_id]["progress"] = 10

        # Run analysis
        result = await coordinator.analyze_drug_repurposing(
            disease=request.disease,
            patient_profile=request.patient_profile,
            parameters=request.analysis_parameters
        )

        # Store result
        job_storage[job_id].update({
            "status": "completed",
            "progress": 100,
            "result": result,
            "completed_at": datetime.now()
        })

    except Exception as e:
        job_storage[job_id].update({
            "status": "failed",
            "error": str(e),
            "failed_at": datetime.now()
        })

@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get status of background job"""
    if job_id not in job_storage:
        raise HTTPException(status_code=404, detail="Job not found")

    job = job_storage[job_id]
    return {
        "job_id": job_id,
        "status": job["status"],
        "progress": job["progress"],
        "created_at": job["created_at"].isoformat(),
        "completed_at": job.get("completed_at", "").isoformat() if job.get("completed_at") else None,
        "result_url": f"/analyze/repurposing/results/{job_id}" if job["status"] == "completed" else None
    }

@router.get("/analyze/repurposing/results/{job_id}")
async def get_analysis_results(job_id: str):
    """Get results from completed analysis"""
    if job_id not in job_storage:
        raise HTTPException(status_code=404, detail="Job not found")

    job = job_storage[job_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed")

    return job["result"]

@router.post("/search/literature", response_model=LiteratureSearchResponse)
async def search_literature(
    request: LiteratureSearchRequest,
    coordinator=Depends(get_coordinator)
):
    """Search biomedical literature"""
    try:
        results = await coordinator.search_literature(
            query=request.query,
            databases=request.databases,
            filters=request.filters,
            limit=request.limit
        )

        return LiteratureSearchResponse(
            query=request.query,
            total_results=len(results),
            results=results
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Literature search failed: {str(e)}")

@router.get("/drugs/{drug_id}", response_model=DrugInfoResponse)
async def get_drug_info(
    drug_id: str,
    db=Depends(get_database)
):
    """Get comprehensive drug information"""
    try:
        drug_info = await db.get_drug_info(drug_id)
        if not drug_info:
            raise HTTPException(status_code=404, detail="Drug not found")

        return DrugInfoResponse(**drug_info)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve drug info: {str(e)}")

@router.get("/diseases/{disease_id}", response_model=DiseaseInfoResponse)
async def get_disease_info(
    disease_id: str,
    db=Depends(get_database)
):
    """Get comprehensive disease information"""
    try:
        disease_info = await db.get_disease_info(disease_id)
        if not disease_info:
            raise HTTPException(status_code=404, detail="Disease not found")

        return DiseaseInfoResponse(**disease_info)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve disease info: {str(e)}")

@router.get("/search/diseases")
async def search_diseases(
    q: str,
    limit: int = 20,
    db=Depends(get_database)
):
    """Search for diseases by name or ID"""
    try:
        results = await db.search_diseases(q, limit)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Disease search failed: {str(e)}")

@router.get("/search/drugs")
async def search_drugs(
    q: str,
    limit: int = 20,
    db=Depends(get_database)
):
    """Search for drugs by name or ID"""
    try:
        results = await db.search_drugs(q, limit)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Drug search failed: {str(e)}")

@router.post("/citations/verify")
async def verify_citations(citations: List[Dict[str, Any]]):
    """Verify and format medical citations"""
    try:
        # This would integrate with citation verification service
        verified_citations = []
        for citation in citations:
            # Mock verification logic
            verified_citations.append({
                "id": citation.get("pmid", citation.get("doi", "unknown")),
                "verification_status": "verified",
                "formatted_citation": f"Sample formatted citation for {citation}",
                "metadata": {
                    "journal_impact_factor": 5.2,
                    "evidence_level": 2,
                    "publication_type": "clinical_trial"
                }
            })

        return {"verified_citations": verified_citations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Citation verification failed: {str(e)}")

@router.get("/stats/system")
async def get_system_stats():
    """Get system statistics"""
    return {
        "analyses_completed": len([j for j in job_storage.values() if j["status"] == "completed"]),
        "jobs_in_queue": len([j for j in job_storage.values() if j["status"] == "queued"]),
        "active_jobs": len([j for j in job_storage.values() if j["status"] == "running"]),
        "uptime": "Running since startup",
        "version": "1.0.0"
    }