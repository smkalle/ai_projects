"""
File Management and Tracking System
Handles batch processing, file tracking, and result organization
"""

import os
import shutil
import hashlib
import json
import io
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import mimetypes
# import magic  # Optional dependency
from PIL import Image
import fitz  # PyMuPDF
import tempfile
import logging

logger = logging.getLogger(__name__)

@dataclass
class FileInfo:
    """Information about a file to be processed"""
    file_path: str
    file_name: str
    file_type: str
    file_size: int
    file_hash: str
    page_count: int
    created_time: str
    modified_time: str
    status: str = "pending"  # pending, processing, completed, failed
    error_message: Optional[str] = None
    result_path: Optional[str] = None
    processing_time: Optional[float] = None
    
    def to_dict(self):
        return asdict(self)

class FileManager:
    """
    Manages files for Dolphin extraction processing
    Handles file tracking, conversion, and result storage
    """
    
    def __init__(self, 
                 input_dir: str = "./input",
                 output_dir: str = "./output",
                 temp_dir: str = "./temp",
                 archive_dir: str = "./archive"):
        
        # Directory setup
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.temp_dir = Path(temp_dir)
        self.archive_dir = Path(archive_dir)
        
        # Create directories
        for dir_path in [self.input_dir, self.output_dir, self.temp_dir, self.archive_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # File tracking
        self.file_registry: Dict[str, FileInfo] = {}
        self.processing_queue: List[str] = []
        self.completed_files: List[str] = []
        self.failed_files: List[str] = []
        
        # Supported formats
        self.supported_formats = {
            '.pdf': 'pdf',
            '.jpg': 'image',
            '.jpeg': 'image',
            '.png': 'image',
            '.tiff': 'image',
            '.tif': 'image',
            '.bmp': 'image'
        }
        
        # Session tracking
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = self.output_dir / self.session_id
        self.session_dir.mkdir(exist_ok=True)
        
        logger.info(f"FileManager initialized - Session: {self.session_id}")
    
    def scan_input_directory(self, 
                           recursive: bool = True,
                           filter_type: Optional[str] = None) -> List[FileInfo]:
        """
        Scan input directory for files to process
        
        Args:
            recursive: Scan subdirectories
            filter_type: Filter by document type (pdf, image, etc.)
            
        Returns:
            List of FileInfo objects
        """
        files_found = []
        
        pattern = "**/*" if recursive else "*"
        
        for file_path in self.input_dir.glob(pattern):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                
                if ext in self.supported_formats:
                    file_type = self.supported_formats[ext]
                    
                    # Apply filter if specified
                    if filter_type and file_type != filter_type:
                        continue
                    
                    try:
                        file_info = self._create_file_info(file_path)
                        files_found.append(file_info)
                        
                        # Register file
                        file_id = self._generate_file_id(file_path)
                        self.file_registry[file_id] = file_info
                        self.processing_queue.append(file_id)
                        
                    except Exception as e:
                        logger.error(f"Error scanning file {file_path}: {e}")
        
        logger.info(f"Found {len(files_found)} files to process")
        return files_found
    
    def add_file(self, file_path: str) -> Optional[FileInfo]:
        """Add a single file to processing queue"""
        path = Path(file_path)
        
        if not path.exists():
            logger.error(f"File not found: {file_path}")
            return None
        
        if path.suffix.lower() not in self.supported_formats:
            logger.error(f"Unsupported file format: {path.suffix}")
            return None
        
        try:
            file_info = self._create_file_info(path)
            file_id = self._generate_file_id(path)
            
            self.file_registry[file_id] = file_info
            self.processing_queue.append(file_id)
            
            logger.info(f"Added file to queue: {path.name}")
            return file_info
            
        except Exception as e:
            logger.error(f"Error adding file {file_path}: {e}")
            return None
    
    def get_next_file(self) -> Optional[Tuple[str, FileInfo]]:
        """Get next file from processing queue"""
        if not self.processing_queue:
            return None
        
        file_id = self.processing_queue.pop(0)
        file_info = self.file_registry.get(file_id)
        
        if file_info:
            file_info.status = "processing"
            return file_id, file_info
        
        return None
    
    def mark_completed(self, 
                      file_id: str,
                      result_path: str,
                      processing_time: float):
        """Mark file as successfully processed"""
        if file_id in self.file_registry:
            file_info = self.file_registry[file_id]
            file_info.status = "completed"
            file_info.result_path = result_path
            file_info.processing_time = processing_time
            
            self.completed_files.append(file_id)
            
            logger.info(f"File completed: {file_info.file_name} ({processing_time:.2f}s)")
    
    def mark_failed(self, file_id: str, error_message: str):
        """Mark file as failed"""
        if file_id in self.file_registry:
            file_info = self.file_registry[file_id]
            file_info.status = "failed"
            file_info.error_message = error_message
            
            self.failed_files.append(file_id)
            
            logger.error(f"File failed: {file_info.file_name} - {error_message}")
    
    def convert_to_images(self, file_path: str) -> List[Image.Image]:
        """
        Convert document to images for processing
        
        Args:
            file_path: Path to document
            
        Returns:
            List of PIL Images (one per page)
        """
        path = Path(file_path)
        images = []
        
        try:
            if path.suffix.lower() == '.pdf':
                # Convert PDF to images
                images = self._pdf_to_images(path)
                
            elif path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp']:
                # Load image directly
                img = Image.open(path)
                images = [img]
                
            else:
                logger.warning(f"Unsupported format for conversion: {path.suffix}")
                
        except Exception as e:
            logger.error(f"Error converting file to images: {e}")
        
        return images
    
    def _pdf_to_images(self, pdf_path: Path, dpi: int = 200) -> List[Image.Image]:
        """Convert PDF pages to images"""
        images = []
        
        try:
            # Open PDF
            pdf_document = fitz.open(str(pdf_path))
            
            for page_num in range(pdf_document.page_count):
                # Get page
                page = pdf_document[page_num]
                
                # Render page to image
                mat = fitz.Matrix(dpi/72, dpi/72)
                pix = page.get_pixmap(matrix=mat)
                
                # Convert to PIL Image
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
                images.append(img)
            
            pdf_document.close()
            
            logger.info(f"Converted PDF to {len(images)} images")
            
        except Exception as e:
            logger.error(f"Error converting PDF to images: {e}")
        
        return images
    
    def save_results(self, 
                    file_id: str,
                    extracted_data: Dict[str, Any],
                    format: str = "json") -> str:
        """
        Save extraction results
        
        Args:
            file_id: File identifier
            extracted_data: Extracted data from Dolphin
            format: Output format (json, csv, etc.)
            
        Returns:
            Path to saved results
        """
        file_info = self.file_registry.get(file_id)
        if not file_info:
            logger.error(f"File not found in registry: {file_id}")
            return ""
        
        # Create output subdirectory for this file
        file_output_dir = self.session_dir / Path(file_info.file_name).stem
        file_output_dir.mkdir(exist_ok=True)
        
        # Save based on format
        if format == "json":
            output_path = file_output_dir / "extracted_data.json"
            with open(output_path, 'w') as f:
                json.dump(extracted_data, f, indent=2, default=str)
                
        elif format == "csv":
            # Convert to CSV format (simplified)
            output_path = file_output_dir / "extracted_data.csv"
            self._save_as_csv(extracted_data, output_path)
            
        else:
            logger.warning(f"Unsupported output format: {format}")
            output_path = file_output_dir / "extracted_data.txt"
            with open(output_path, 'w') as f:
                f.write(str(extracted_data))
        
        logger.info(f"Results saved to: {output_path}")
        return str(output_path)
    
    def _save_as_csv(self, data: Dict[str, Any], output_path: Path):
        """Save data in CSV format"""
        import pandas as pd
        
        try:
            # Flatten nested data for CSV
            flattened = {}
            
            if "aggregated_data" in data:
                agg = data["aggregated_data"]
                
                # Patient info
                if "patient_info" in agg:
                    for key, value in agg["patient_info"].items():
                        flattened[f"patient_{key}"] = value
                
                # Medications
                if "medications" in agg:
                    for i, med in enumerate(agg["medications"]):
                        for key, value in med.items():
                            flattened[f"medication_{i}_{key}"] = value
                
                # Lab results
                if "lab_results" in agg:
                    for i, lab in enumerate(agg["lab_results"]):
                        if "rows" in lab:
                            for j, row in enumerate(lab["rows"]):
                                flattened[f"lab_{i}_row_{j}"] = ", ".join(map(str, row))
            
            # Convert to DataFrame and save
            df = pd.DataFrame([flattened])
            df.to_csv(output_path, index=False)
            
        except Exception as e:
            logger.error(f"Error saving CSV: {e}")
    
    def archive_processed_file(self, file_id: str, keep_original: bool = False):
        """Move processed file to archive"""
        file_info = self.file_registry.get(file_id)
        if not file_info:
            return
        
        source_path = Path(file_info.file_path)
        if not source_path.exists():
            return
        
        # Create archive subdirectory
        archive_subdir = self.archive_dir / self.session_id
        archive_subdir.mkdir(exist_ok=True)
        
        # Move or copy file
        dest_path = archive_subdir / source_path.name
        
        if keep_original:
            shutil.copy2(source_path, dest_path)
            logger.info(f"Copied to archive: {source_path.name}")
        else:
            shutil.move(str(source_path), str(dest_path))
            logger.info(f"Moved to archive: {source_path.name}")
    
    def cleanup_temp_files(self):
        """Clean up temporary files"""
        try:
            for temp_file in self.temp_dir.glob("*"):
                if temp_file.is_file():
                    temp_file.unlink()
                elif temp_file.is_dir():
                    shutil.rmtree(temp_file)
            
            logger.info("Temporary files cleaned up")
            
        except Exception as e:
            logger.error(f"Error cleaning temp files: {e}")
    
    def _create_file_info(self, file_path: Path) -> FileInfo:
        """Create FileInfo object for a file"""
        stat = file_path.stat()
        
        # Calculate file hash
        file_hash = self._calculate_file_hash(file_path)
        
        # Get page count
        page_count = self._get_page_count(file_path)
        
        return FileInfo(
            file_path=str(file_path),
            file_name=file_path.name,
            file_type=self.supported_formats.get(file_path.suffix.lower(), "unknown"),
            file_size=stat.st_size,
            file_hash=file_hash,
            page_count=page_count,
            created_time=datetime.fromtimestamp(stat.st_ctime).isoformat(),
            modified_time=datetime.fromtimestamp(stat.st_mtime).isoformat()
        )
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    
    def _get_page_count(self, file_path: Path) -> int:
        """Get page count for document"""
        try:
            if file_path.suffix.lower() == '.pdf':
                pdf = fitz.open(str(file_path))
                count = pdf.page_count
                pdf.close()
                return count
            else:
                return 1  # Single page for images
                
        except Exception as e:
            logger.warning(f"Could not determine page count: {e}")
            return 0
    
    def _generate_file_id(self, file_path: Path) -> str:
        """Generate unique file ID"""
        return f"{self.session_id}_{file_path.stem}_{hashlib.md5(str(file_path).encode()).hexdigest()[:8]}"
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get current processing statistics"""
        total_files = len(self.file_registry)
        
        return {
            "session_id": self.session_id,
            "total_files": total_files,
            "pending": len(self.processing_queue),
            "processing": sum(1 for f in self.file_registry.values() if f.status == "processing"),
            "completed": len(self.completed_files),
            "failed": len(self.failed_files),
            "success_rate": len(self.completed_files) / total_files if total_files > 0 else 0,
            "total_pages": sum(f.page_count for f in self.file_registry.values()),
            "total_size_mb": sum(f.file_size for f in self.file_registry.values()) / (1024 * 1024)
        }
    
    def save_file_registry(self):
        """Save file registry to JSON"""
        registry_path = self.session_dir / "file_registry.json"
        
        registry_data = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "files": {
                file_id: file_info.to_dict() 
                for file_id, file_info in self.file_registry.items()
            },
            "statistics": self.get_processing_stats()
        }
        
        with open(registry_path, 'w') as f:
            json.dump(registry_data, f, indent=2, default=str)
        
        logger.info(f"File registry saved to: {registry_path}")
        return str(registry_path)

class BatchProcessor:
    """Handles batch processing of multiple files"""
    
    def __init__(self, 
                 file_manager: FileManager,
                 max_parallel: int = 1):
        
        self.file_manager = file_manager
        self.max_parallel = max_parallel
        self.current_batch = []
        
    def create_batches(self, batch_size: int = 10) -> List[List[str]]:
        """Create batches of files for processing"""
        batches = []
        queue = self.file_manager.processing_queue.copy()
        
        while queue:
            batch = queue[:batch_size]
            queue = queue[batch_size:]
            batches.append(batch)
        
        logger.info(f"Created {len(batches)} batches with size {batch_size}")
        return batches
    
    def process_batch(self, batch: List[str], process_func) -> Dict[str, Any]:
        """
        Process a batch of files
        
        Args:
            batch: List of file IDs
            process_func: Function to process each file
            
        Returns:
            Batch results
        """
        results = {}
        
        for file_id in batch:
            file_info = self.file_manager.file_registry.get(file_id)
            if not file_info:
                continue
            
            try:
                # Process file
                result = process_func(file_info.file_path)
                results[file_id] = {
                    "success": True,
                    "data": result
                }
                
            except Exception as e:
                results[file_id] = {
                    "success": False,
                    "error": str(e)
                }
        
        return results