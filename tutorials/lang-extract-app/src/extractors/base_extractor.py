"""Base extractor module for LangExtract operations."""

import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import json
from datetime import datetime
from langextract import LangExtract
import hashlib

from config.settings import settings


logger = logging.getLogger(__name__)


class ExtractionResult:
    """Container for extraction results with metadata."""
    
    def __init__(self, 
                 extractions: List[Dict[str, Any]],
                 source_file: str,
                 template_used: str,
                 processing_time: float,
                 token_count: Optional[int] = None):
        self.extractions = extractions
        self.source_file = source_file
        self.template_used = template_used
        self.processing_time = processing_time
        self.token_count = token_count
        self.timestamp = datetime.now()
        self.id = self._generate_id()
    
    def _generate_id(self) -> str:
        """Generate unique ID for this extraction."""
        content = f"{self.source_file}{self.timestamp}{len(self.extractions)}"
        return hashlib.md5(content.encode()).hexdigest()[:8]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "id": self.id,
            "source_file": self.source_file,
            "template_used": self.template_used,
            "processing_time": self.processing_time,
            "token_count": self.token_count,
            "timestamp": self.timestamp.isoformat(),
            "extraction_count": len(self.extractions),
            "extractions": self.extractions
        }


class BaseExtractor:
    """Base class for document extraction using LangExtract."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the extractor with optional API key."""
        self.api_key = api_key or settings.langextract_api_key
        self.lx = None
        self._initialize_langextract()
        
    def _initialize_langextract(self):
        """Initialize LangExtract instance."""
        try:
            if self.api_key:
                import os
                os.environ["LANGEXTRACT_API_KEY"] = self.api_key
            self.lx = LangExtract()
            logger.info("LangExtract initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize LangExtract: {e}")
            raise
    
    def extract_from_text(self,
                         text: str,
                         prompt: str,
                         source_name: str = "direct_input",
                         **kwargs) -> ExtractionResult:
        """Extract information from text using given prompt."""
        logger.info(f"Starting extraction from text (length: {len(text)})")
        
        import time
        start_time = time.time()
        
        try:
            # Configure extraction parameters
            extraction_params = {
                "text": text,
                "instructions": prompt,
                "max_workers": kwargs.get("max_workers", 10),
                "extraction_passes": kwargs.get("extraction_passes", 2),
                "max_char_buffer": kwargs.get("max_char_buffer", 1000)
            }
            
            # Perform extraction
            result = self.lx.extract(**extraction_params)
            
            # Process results
            extractions = []
            if hasattr(result, 'extractions'):
                extractions = result.extractions
            elif isinstance(result, list):
                extractions = result
            elif isinstance(result, dict) and 'extractions' in result:
                extractions = result['extractions']
            
            processing_time = time.time() - start_time
            
            return ExtractionResult(
                extractions=extractions,
                source_file=source_name,
                template_used="custom_prompt",
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            raise
    
    def extract_from_file(self,
                         file_path: Path,
                         prompt: str,
                         **kwargs) -> ExtractionResult:
        """Extract information from file using given prompt."""
        logger.info(f"Starting extraction from file: {file_path}")
        
        # Read file content based on type
        text = self._read_file_content(file_path)
        
        return self.extract_from_text(
            text=text,
            prompt=prompt,
            source_name=file_path.name,
            **kwargs
        )
    
    def extract_from_url(self,
                        url: str,
                        prompt: str,
                        **kwargs) -> ExtractionResult:
        """Extract information from URL using given prompt."""
        logger.info(f"Starting extraction from URL: {url}")
        
        import time
        start_time = time.time()
        
        try:
            extraction_params = {
                "url": url,
                "instructions": prompt,
                "max_workers": kwargs.get("max_workers", 10),
                "extraction_passes": kwargs.get("extraction_passes", 2),
                "max_char_buffer": kwargs.get("max_char_buffer", 1000)
            }
            
            result = self.lx.extract(**extraction_params)
            
            # Process results
            extractions = []
            if hasattr(result, 'extractions'):
                extractions = result.extractions
            elif isinstance(result, list):
                extractions = result
            elif isinstance(result, dict) and 'extractions' in result:
                extractions = result['extractions']
            
            processing_time = time.time() - start_time
            
            return ExtractionResult(
                extractions=extractions,
                source_file=url,
                template_used="custom_prompt",
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"URL extraction failed: {e}")
            raise
    
    def _read_file_content(self, file_path: Path) -> str:
        """Read content from various file types."""
        suffix = file_path.suffix.lower()
        
        try:
            if suffix == '.txt':
                return file_path.read_text(encoding='utf-8')
            
            elif suffix == '.pdf':
                import PyPDF2
                text = ""
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                return text
            
            elif suffix == '.docx':
                from docx import Document
                doc = Document(file_path)
                return "\n".join([para.text for para in doc.paragraphs])
            
            elif suffix in ['.html', '.htm']:
                from bs4 import BeautifulSoup
                html_content = file_path.read_text(encoding='utf-8')
                soup = BeautifulSoup(html_content, 'html.parser')
                return soup.get_text()
            
            else:
                raise ValueError(f"Unsupported file type: {suffix}")
                
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            raise
    
    def save_results(self, result: ExtractionResult, output_path: Path):
        """Save extraction results to JSON file."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
            logger.info(f"Results saved to: {output_path}")
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
            raise