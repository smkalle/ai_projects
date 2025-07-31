"""Error handling and logging utilities."""

import logging
import traceback
from functools import wraps
from typing import Any, Callable, Optional
import streamlit as st
from datetime import datetime
from pathlib import Path


# Configure logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f"langextract_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class LangExtractError(Exception):
    """Base exception for LangExtract application."""
    pass


class FileProcessingError(LangExtractError):
    """Error during file processing."""
    pass


class ExtractionError(LangExtractError):
    """Error during data extraction."""
    pass


class ExportError(LangExtractError):
    """Error during data export."""
    pass


class APIError(LangExtractError):
    """Error with API communication."""
    pass


def handle_errors(func: Callable) -> Callable:
    """Decorator to handle errors in Streamlit functions."""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except FileProcessingError as e:
            logger.error(f"File processing error in {func.__name__}: {e}")
            st.error(f"📁 File Processing Error: {str(e)}")
            st.info("Please check the file format and try again.")
        except ExtractionError as e:
            logger.error(f"Extraction error in {func.__name__}: {e}")
            st.error(f"🔍 Extraction Error: {str(e)}")
            st.info("The extraction process failed. Please check your template and try again.")
        except ExportError as e:
            logger.error(f"Export error in {func.__name__}: {e}")
            st.error(f"💾 Export Error: {str(e)}")
            st.info("Failed to export data. Please try a different format.")
        except APIError as e:
            logger.error(f"API error in {func.__name__}: {e}")
            st.error(f"🌐 API Error: {str(e)}")
            st.info("Please check your API key and internet connection.")
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}\n{traceback.format_exc()}")
            st.error(f"❌ Unexpected Error: {str(e)}")
            st.info("An unexpected error occurred. Please check the logs for details.")
            
            # Show debug info in development mode
            if st.secrets.get("debug", False):
                with st.expander("Debug Information"):
                    st.code(traceback.format_exc())
        
        return None
    
    return wrapper


def log_extraction_metrics(
    source_file: str,
    template: str,
    extraction_count: int,
    processing_time: float,
    success: bool,
    error_message: Optional[str] = None
):
    """Log extraction metrics for monitoring."""
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "source_file": source_file,
        "template": template,
        "extraction_count": extraction_count,
        "processing_time": processing_time,
        "success": success,
        "error_message": error_message
    }
    
    if success:
        logger.info(f"Extraction completed: {metrics}")
    else:
        logger.error(f"Extraction failed: {metrics}")


def validate_api_key(api_key: str) -> bool:
    """Validate API key format."""
    if not api_key:
        raise APIError("API key is required for cloud processing")
    
    if len(api_key) < 20:
        raise APIError("Invalid API key format")
    
    return True


def validate_file_upload(file, max_size_mb: int = 10) -> bool:
    """Validate uploaded file."""
    if not file:
        raise FileProcessingError("No file uploaded")
    
    # Check file size
    file_size = file.size if hasattr(file, 'size') else len(file.getvalue())
    if file_size > max_size_mb * 1024 * 1024:
        raise FileProcessingError(f"File size exceeds {max_size_mb}MB limit")
    
    # Check file extension
    file_ext = Path(file.name).suffix.lower().lstrip('.')
    supported_types = ["pdf", "txt", "docx", "html"]
    
    if file_ext not in supported_types:
        raise FileProcessingError(f"Unsupported file type: {file_ext}")
    
    return True


def create_user_friendly_error(error: Exception) -> str:
    """Convert technical errors to user-friendly messages."""
    error_mappings = {
        "rate limit": "You've exceeded the API rate limit. Please wait a moment and try again.",
        "api key": "Invalid API key. Please check your Gemini API key in the settings.",
        "connection": "Connection error. Please check your internet connection.",
        "timeout": "The request timed out. Try processing smaller documents or fewer files.",
        "memory": "Out of memory. Try processing fewer files at once.",
        "permission": "Permission denied. Please check file permissions.",
        "not found": "File not found. Please upload the file again.",
        "encoding": "File encoding error. Please ensure the file uses UTF-8 encoding.",
        "quota": "API quota exceeded. Please check your Gemini account limits."
    }
    
    error_str = str(error).lower()
    
    for key, message in error_mappings.items():
        if key in error_str:
            return message
    
    return f"An error occurred: {str(error)}"


class ErrorCollector:
    """Collect and aggregate errors for batch operations."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def add_error(self, source: str, error: Exception):
        """Add an error to the collection."""
        self.errors.append({
            "source": source,
            "error": str(error),
            "type": type(error).__name__,
            "timestamp": datetime.now()
        })
    
    def add_warning(self, source: str, message: str):
        """Add a warning to the collection."""
        self.warnings.append({
            "source": source,
            "message": message,
            "timestamp": datetime.now()
        })
    
    def has_errors(self) -> bool:
        """Check if any errors were collected."""
        return len(self.errors) > 0
    
    def get_summary(self) -> dict:
        """Get error summary."""
        return {
            "total_errors": len(self.errors),
            "total_warnings": len(self.warnings),
            "error_types": list(set(e["type"] for e in self.errors)),
            "affected_sources": list(set(e["source"] for e in self.errors))
        }
    
    def display_in_streamlit(self):
        """Display errors and warnings in Streamlit."""
        if self.errors:
            st.error(f"⚠️ {len(self.errors)} error(s) occurred during processing")
            with st.expander("Error Details"):
                for error in self.errors:
                    st.write(f"**{error['source']}**: {error['error']}")
        
        if self.warnings:
            st.warning(f"ℹ️ {len(self.warnings)} warning(s) during processing")
            with st.expander("Warning Details"):
                for warning in self.warnings:
                    st.write(f"**{warning['source']}**: {warning['message']}")


# Global error collector instance
error_collector = ErrorCollector()