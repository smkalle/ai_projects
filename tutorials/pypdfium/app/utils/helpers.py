"""
Utility functions for Energy Document AI
"""

import os
import hashlib
import mimetypes
from typing import List, Dict, Optional, Tuple
import logging
from datetime import datetime
import pandas as pd

logger = logging.getLogger(__name__)

def setup_logging(debug: bool = False) -> None:
    """Setup logging configuration"""
    level = logging.DEBUG if debug else logging.INFO

    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def calculate_file_hash(file_path: str) -> str:
    """Calculate SHA-256 hash of a file"""
    hash_sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except Exception as e:
        logger.error(f"Error calculating hash for {file_path}: {e}")
        return ""

def validate_pdf_file(file_path: str, max_size_mb: int = 50) -> Tuple[bool, str]:
    """Validate PDF file"""
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            return False, "File does not exist"

        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size > max_size_mb * 1024 * 1024:
            return False, f"File size exceeds {max_size_mb}MB limit"

        # Check mime type
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type != "application/pdf":
            return False, "File is not a PDF"

        return True, "Valid PDF file"

    except Exception as e:
        return False, f"Error validating file: {e}"

def classify_document_content(text: str, keywords_dict: Dict[str, List[str]]) -> str:
    """Classify document based on content keywords"""
    text_lower = text.lower()
    scores = {}

    for category, keywords in keywords_dict.items():
        score = sum(1 for keyword in keywords if keyword in text_lower)
        if score > 0:
            scores[category] = score

    if scores:
        return max(scores.items(), key=lambda x: x[1])[0]
    else:
        return "general"

def extract_technical_metrics(text: str) -> List[Dict[str, str]]:
    """Extract technical metrics and measurements from text"""
    import re

    # Common energy units and measurements
    patterns = [
        r'(\d+(?:\.\d+)?\s*(?:MW|MWh|kW|kWh|GW|GWh|V|A|Hz|°C|°F|%|psi|bar))',
        r'(\d+(?:\.\d+)?\s*(?:efficiency|capacity factor|load factor))',
        r'(NERC|FERC|EPA|IEEE|IEC)\s+([A-Z0-9-]+)',
    ]

    metrics = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                metrics.append({"type": "regulation", "value": " ".join(match)})
            else:
                metrics.append({"type": "measurement", "value": match})

    return metrics

def create_document_summary(metadata: Dict) -> str:
    """Create a summary of document metadata"""
    summary = f"Document: {metadata.get('name', 'Unknown')}\n"
    summary += f"Type: {metadata.get('type', 'Unknown')}\n"
    summary += f"Size: {metadata.get('size', 0):,} bytes\n"
    summary += f"Pages: {metadata.get('pages', 'Unknown')}\n"
    summary += f"Processed: {metadata.get('timestamp', 'Unknown')}\n"

    if 'hash' in metadata:
        summary += f"Hash: {metadata['hash'][:16]}...\n"

    return summary

def format_search_results(results: List[Dict]) -> pd.DataFrame:
    """Format search results as a DataFrame"""
    if not results:
        return pd.DataFrame()

    formatted_results = []
    for i, result in enumerate(results):
        formatted_results.append({
            'Rank': i + 1,
            'Score': f"{result['score']:.3f}",
            'Document': result['document_name'],
            'Type': result['document_type'],
            'Content Preview': result['content'][:200] + "..." if len(result['content']) > 200 else result['content']
        })

    return pd.DataFrame(formatted_results)

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    import re
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\|?*]', '_', filename)
    # Limit length
    name, ext = os.path.splitext(filename)
    if len(name) > 100:
        name = name[:100]
    return f"{name}{ext}"

def estimate_processing_cost(num_pages: int, dpi: int = 300) -> float:
    """Estimate OpenAI API cost for processing PDF"""
    # Rough estimation based on image size and GPT-4o pricing
    # This is an approximation - actual costs may vary
    base_cost_per_page = 0.02  # Approximate cost per page
    dpi_multiplier = dpi / 300  # Adjust for DPI

    return num_pages * base_cost_per_page * dpi_multiplier

def get_system_info() -> Dict[str, str]:
    """Get system information for diagnostics"""
    import platform
    import psutil

    return {
        "platform": platform.system(),
        "python_version": platform.python_version(),
        "cpu_count": str(os.cpu_count()),
        "memory_gb": f"{psutil.virtual_memory().total / (1024**3):.1f}",
        "timestamp": datetime.now().isoformat()
    }
