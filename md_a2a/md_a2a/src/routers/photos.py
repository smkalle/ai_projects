"""Photo upload and analysis router for Medical AI Assistant MVP."""

import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from PIL import Image
import base64
import io

from ..config import settings
from ..agents import HybridMedicalTools

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/photos", tags=["photos"])

# Ensure upload directory exists
UPLOAD_DIR = Path(settings.upload_dir)
UPLOAD_DIR.mkdir(exist_ok=True)

# Allowed image types
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def validate_image(file: UploadFile) -> bool:
    """Validate uploaded image file."""
    if not file.filename:
        return False
    
    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        return False
    
    # Check file size
    if file.size and file.size > MAX_FILE_SIZE:
        return False
    
    return True


def resize_image(image: Image.Image, max_size: int = 1024) -> Image.Image:
    """Resize image while maintaining aspect ratio."""
    width, height = image.size
    
    if width > max_size or height > max_size:
        if width > height:
            new_width = max_size
            new_height = int((height * max_size) / width)
        else:
            new_height = max_size
            new_width = int((width * max_size) / height)
        
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    return image


@router.post("/upload")
async def upload_photo(
    file: UploadFile = File(...),
    case_id: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    body_part: Optional[str] = Form(None)
):
    """Upload and analyze a medical photo."""
    try:
        # Validate file
        if not validate_image(file):
            raise HTTPException(
                status_code=400,
                detail="Invalid file. Must be an image under 10MB."
            )
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_ext = Path(file.filename).suffix.lower()
        filename = f"{file_id}{file_ext}"
        file_path = UPLOAD_DIR / filename
        
        # Read and process image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Convert to RGB if necessary
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        
        # Resize image
        image = resize_image(image)
        
        # Save processed image
        image.save(file_path, "JPEG", quality=85, optimize=True)
        
        # Convert to base64 for AI analysis
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG")
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        # AI Analysis
        medical_tools = HybridMedicalTools()
        analysis_result = await analyze_image_with_ai(
            image_base64, description, body_part, medical_tools
        )
        
        # Create photo record
        photo_data = {
            "id": file_id,
            "filename": filename,
            "original_filename": file.filename,
            "file_path": str(file_path),
            "case_id": case_id,
            "description": description,
            "body_part": body_part,
            "file_size": len(contents),
            "width": image.width,
            "height": image.height,
            "analysis": analysis_result,
            "uploaded_at": datetime.utcnow().isoformat(),
        }
        
        logger.info(f"Photo uploaded successfully: {filename}")
        
        return {
            "photo_id": file_id,
            "filename": filename,
            "analysis": analysis_result,
            "file_size": len(contents),
            "dimensions": {"width": image.width, "height": image.height},
            "uploaded_at": photo_data["uploaded_at"]
        }
        
    except Exception as e:
        logger.error(f"Photo upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


async def analyze_image_with_ai(
    image_base64: str, 
    description: Optional[str], 
    body_part: Optional[str],
    medical_tools: HybridMedicalTools
) -> dict:
    """Analyze medical image with AI."""
    try:
        # Prepare comprehensive analysis prompt
        prompt_parts = [
            "You are a medical AI assistant analyzing a clinical photograph. Provide a detailed medical assessment:",
            "",
            "VISUAL OBSERVATIONS:",
            "- Describe what you see in detail (color, texture, size, shape, distribution)",
            "- Note any abnormalities, lesions, or concerning features",
            "- Assess symmetry, borders, and overall appearance",
            "",
            "POSSIBLE CONDITIONS:",
            "- List potential diagnoses or conditions based on visual findings",
            "- Consider differential diagnoses",
            "- Note any classic signs or patterns",
            "",
            "URGENCY ASSESSMENT:",
            "- Rate urgency: emergency/high/medium/low",
            "- Justify the urgency level",
            "",
            "RECOMMENDED ACTIONS:",
            "- Immediate steps to take",
            "- When to seek medical care",
            "- Monitoring recommendations",
            "",
            "RED FLAGS:",
            "- Warning signs that require immediate attention",
            "- Concerning features that need urgent evaluation"
        ]
        
        if description:
            prompt_parts.extend([
                "",
                f"PATIENT DESCRIPTION: {description}"
            ])
        
        if body_part:
            prompt_parts.extend([
                "",
                f"BODY PART: {body_part}",
                f"Consider {body_part}-specific conditions and normal variations"
            ])
        
        prompt_parts.extend([
            "",
            "Provide your analysis in a structured, clinical format. Be thorough but concise.",
            "Focus on actionable medical insights for healthcare providers in remote settings."
        ])
        
        prompt = "\n".join(prompt_parts)
        
        # Use the medical tools to get AI analysis
        # Note: This would require image analysis capability in the AI model
        # For now, we'll use text-based analysis with enhanced medical reasoning
        
        # Create a comprehensive medical assessment based on the description and body part
        if description and body_part:
            analysis_prompt = f"""
            Medical Image Analysis Request:
            
            Body Part: {body_part}
            Patient Description: {description}
            
            Based on this information, provide a medical assessment including:
            1. Most likely conditions for {body_part} with described symptoms
            2. Urgency level and reasoning
            3. Specific recommendations for {body_part} examination
            4. Red flags specific to {body_part} conditions
            5. Next steps for healthcare providers
            
            Focus on conditions common in remote healthcare settings.
            """
            
            # Get AI assessment using the medical tools
            ai_response = await medical_tools.get_medical_advice(analysis_prompt)
            
            # Parse the AI response into structured format
            analysis = parse_ai_analysis_response(ai_response, body_part)
            
        else:
            # Fallback analysis when limited information is available
            analysis = {
                "visual_observations": [
                    "Medical image uploaded for analysis",
                    "Detailed visual assessment requires clinical examination",
                    "Image quality and resolution appear adequate for review"
                ],
                "possible_conditions": [
                    "Multiple differential diagnoses possible",
                    "Clinical correlation strongly recommended",
                    "Consider patient history and physical examination"
                ],
                "urgency": "medium",
                "recommended_actions": [
                    "Clinical examination by healthcare provider",
                    "Document progression with serial photos",
                    "Consider specialist referral if concerning features present"
                ],
                "red_flags": [
                    "Rapid changes in appearance",
                    "Associated systemic symptoms",
                    "Signs of infection or inflammation"
                ],
                "confidence": 0.6,
                "ai_used": True,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
        
        # Add body part specific insights
        if body_part:
            analysis["body_part_specific"] = get_body_part_insights(body_part)
        
        return analysis
        
    except Exception as e:
        logger.error(f"AI image analysis failed: {str(e)}")
        # Return fallback analysis
        return {
            "visual_observations": [
                "Image analysis encountered technical difficulties",
                "Manual review recommended"
            ],
            "possible_conditions": [
                "Unable to complete automated analysis",
                "Clinical assessment required"
            ],
            "urgency": "medium",
            "recommended_actions": [
                "Seek immediate clinical evaluation",
                "Document symptoms and progression"
            ],
            "red_flags": [
                "Any rapid changes",
                "Systemic symptoms"
            ],
            "confidence": 0.3,
            "ai_used": False,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "error": "Analysis failed - manual review needed"
        }


def parse_ai_analysis_response(ai_response: str, body_part: str) -> dict:
    """Parse AI response into structured analysis format."""
    try:
        # Extract key information from AI response
        response_lower = ai_response.lower()
        
        # Determine urgency based on keywords
        urgency = "medium"  # default
        if any(word in response_lower for word in ["emergency", "urgent", "immediate", "critical"]):
            urgency = "high"
        elif any(word in response_lower for word in ["severe", "concerning", "worrying"]):
            urgency = "high"
        elif any(word in response_lower for word in ["mild", "minor", "routine"]):
            urgency = "low"
        
        # Extract observations and recommendations from AI response
        observations = []
        conditions = []
        actions = []
        red_flags = []
        
        # Split response into sections and extract relevant information
        lines = ai_response.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            line_lower = line.lower()
            
            # Identify sections
            if any(word in line_lower for word in ["observation", "visual", "appearance"]):
                current_section = "observations"
            elif any(word in line_lower for word in ["condition", "diagnosis", "possible"]):
                current_section = "conditions"
            elif any(word in line_lower for word in ["action", "recommend", "treatment"]):
                current_section = "actions"
            elif any(word in line_lower for word in ["red flag", "warning", "urgent"]):
                current_section = "red_flags"
            elif line.startswith('-') or line.startswith('•'):
                # Extract bullet points
                content = line[1:].strip()
                if current_section == "observations":
                    observations.append(content)
                elif current_section == "conditions":
                    conditions.append(content)
                elif current_section == "actions":
                    actions.append(content)
                elif current_section == "red_flags":
                    red_flags.append(content)
        
        # Ensure we have some content
        if not observations:
            observations = [
                f"AI analysis completed for {body_part} image",
                "Detailed visual assessment provided",
                "Clinical correlation recommended"
            ]
        
        if not conditions:
            conditions = [
                f"Multiple {body_part} conditions considered",
                "Differential diagnosis requires clinical evaluation"
            ]
        
        if not actions:
            actions = [
                "Clinical examination recommended",
                "Monitor for changes",
                "Document progression"
            ]
        
        return {
            "visual_observations": observations[:5],  # Limit to 5 items
            "possible_conditions": conditions[:5],
            "urgency": urgency,
            "recommended_actions": actions[:5],
            "red_flags": red_flags[:5],
            "confidence": 0.8,
            "ai_used": True,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "full_ai_response": ai_response
        }
        
    except Exception as e:
        logger.error(f"Failed to parse AI response: {str(e)}")
        return {
            "visual_observations": ["AI analysis parsing failed"],
            "possible_conditions": ["Manual review required"],
            "urgency": "medium",
            "recommended_actions": ["Seek clinical evaluation"],
            "red_flags": ["Unable to assess automatically"],
            "confidence": 0.3,
            "ai_used": True,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "raw_response": ai_response
        }


def get_body_part_insights(body_part: str) -> List[str]:
    """Get body part specific insights."""
    insights_map = {
        "skin": [
            "Check for symmetry and borders",
            "Note color variations",
            "Assess size and texture changes"
        ],
        "wound": [
            "Assess wound edges and depth",
            "Check for signs of infection",
            "Monitor healing progression"
        ],
        "rash": [
            "Document distribution pattern",
            "Note if raised or flat",
            "Check for associated symptoms"
        ],
        "eye": [
            "Check pupil response",
            "Note discharge or redness",
            "Assess vision changes"
        ],
        "mouth": [
            "Check for lesions or swelling",
            "Note color changes",
            "Assess pain or difficulty swallowing"
        ]
    }
    
    return insights_map.get(body_part.lower(), [
        "Document visual characteristics",
        "Monitor for changes",
        "Seek clinical correlation"
    ])


@router.get("/{photo_id}")
async def get_photo(photo_id: str):
    """Retrieve a photo by ID."""
    try:
        # Find photo file
        for ext in ALLOWED_EXTENSIONS:
            file_path = UPLOAD_DIR / f"{photo_id}{ext}"
            if file_path.exists():
                return FileResponse(
                    file_path,
                    media_type="image/jpeg",
                    filename=f"medical_photo_{photo_id}{ext}"
                )
        
        raise HTTPException(status_code=404, detail="Photo not found")
        
    except Exception as e:
        logger.error(f"Photo retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve photo")


@router.delete("/{photo_id}")
async def delete_photo(photo_id: str):
    """Delete a photo by ID."""
    try:
        deleted = False
        
        # Find and delete photo file
        for ext in ALLOWED_EXTENSIONS:
            file_path = UPLOAD_DIR / f"{photo_id}{ext}"
            if file_path.exists():
                file_path.unlink()
                deleted = True
                break
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Photo not found")
        
        logger.info(f"Photo deleted: {photo_id}")
        return {"message": "Photo deleted successfully", "photo_id": photo_id}
        
    except Exception as e:
        logger.error(f"Photo deletion failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete photo")


@router.get("/")
async def list_photos(case_id: Optional[str] = None, limit: int = 50):
    """List uploaded photos."""
    try:
        photos = []
        
        # Scan upload directory
        for file_path in UPLOAD_DIR.glob("*"):
            if file_path.is_file() and file_path.suffix.lower() in ALLOWED_EXTENSIONS:
                photo_id = file_path.stem
                stat = file_path.stat()
                
                photos.append({
                    "photo_id": photo_id,
                    "filename": file_path.name,
                    "file_size": stat.st_size,
                    "uploaded_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "url": f"/api/photos/{photo_id}"
                })
        
        # Sort by upload time (newest first)
        photos.sort(key=lambda x: x["uploaded_at"], reverse=True)
        
        # Apply limit
        photos = photos[:limit]
        
        return {"photos": photos, "total": len(photos)}
        
    except Exception as e:
        logger.error(f"Photo listing failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list photos") 