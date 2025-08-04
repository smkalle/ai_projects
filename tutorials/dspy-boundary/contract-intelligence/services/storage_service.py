"""Document storage service for managing uploaded files."""

import os
import json
import hashlib
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

from config.settings import settings
from services.document_parser import ParsedDocument, DocumentMetadata


@dataclass
class StoredDocument:
    """Stored document information."""
    doc_id: str
    original_filename: str
    stored_filename: str
    file_path: str
    metadata_path: str
    upload_timestamp: datetime
    file_size: int
    file_hash: str
    metadata: DocumentMetadata
    processing_status: str = "uploaded"  # uploaded, processing, completed, error


class StorageError(Exception):
    """Custom exception for storage operations."""
    pass


class StorageService:
    """Service for managing document storage and retrieval."""
    
    def __init__(self):
        self.upload_dir = Path(settings.upload_dir)
        self.processed_dir = Path(settings.processed_dir)
        self.exports_dir = Path(settings.exports_dir)
        
        # Ensure directories exist
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure all required directories exist."""
        for directory in [self.upload_dir, self.processed_dir, self.exports_dir]:
            directory.mkdir(parents=True, exist_ok=True)
            
            # Create .gitkeep files
            gitkeep = directory / ".gitkeep"
            if not gitkeep.exists():
                gitkeep.touch()
    
    def store_document(self, file_data: bytes, filename: str, 
                      parsed_doc: Optional[ParsedDocument] = None) -> StoredDocument:
        """
        Store uploaded document and its metadata.
        
        Args:
            file_data: Raw file bytes
            filename: Original filename
            parsed_doc: Parsed document data (optional)
            
        Returns:
            StoredDocument with storage information
            
        Raises:
            StorageError: If storage fails
        """
        try:
            # Generate document ID and file hash
            file_hash = hashlib.sha256(file_data).hexdigest()
            doc_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file_hash[:8]}"
            
            # Check if file already exists (deduplication)
            existing_doc = self._find_by_hash(file_hash)
            if existing_doc:
                return existing_doc
            
            # Generate stored filename
            file_ext = Path(filename).suffix.lower()
            stored_filename = f"{doc_id}{file_ext}"
            
            # Store file
            file_path = self.upload_dir / stored_filename
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            # Create metadata
            metadata_filename = f"{doc_id}_metadata.json"
            metadata_path = self.upload_dir / metadata_filename
            
            # Create stored document record
            stored_doc = StoredDocument(
                doc_id=doc_id,
                original_filename=filename,
                stored_filename=stored_filename,
                file_path=str(file_path),
                metadata_path=str(metadata_path),
                upload_timestamp=datetime.now(),
                file_size=len(file_data),
                file_hash=file_hash,
                metadata=parsed_doc.metadata if parsed_doc else self._create_basic_metadata(filename, file_data),
                processing_status="uploaded"
            )
            
            # Store metadata
            self._save_metadata(stored_doc)
            
            return stored_doc
            
        except Exception as e:
            raise StorageError(f"Failed to store document: {str(e)}")
    
    def get_document(self, doc_id: str) -> Optional[StoredDocument]:
        """Get document by ID."""
        try:
            metadata_path = self.upload_dir / f"{doc_id}_metadata.json"
            if not metadata_path.exists():
                return None
            
            return self._load_metadata(metadata_path)
            
        except Exception as e:
            raise StorageError(f"Failed to retrieve document {doc_id}: {str(e)}")
    
    def list_documents(self, limit: Optional[int] = None) -> List[StoredDocument]:
        """List all stored documents."""
        try:
            documents = []
            
            # Find all metadata files
            for metadata_file in self.upload_dir.glob("*_metadata.json"):
                try:
                    doc = self._load_metadata(metadata_file)
                    documents.append(doc)
                except Exception:
                    continue  # Skip corrupted metadata
            
            # Sort by upload timestamp (newest first)
            documents.sort(key=lambda x: x.upload_timestamp, reverse=True)
            
            if limit:
                documents = documents[:limit]
            
            return documents
            
        except Exception as e:
            raise StorageError(f"Failed to list documents: {str(e)}")
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete document and its metadata."""
        try:
            doc = self.get_document(doc_id)
            if not doc:
                return False
            
            # Delete files
            file_path = Path(doc.file_path)
            metadata_path = Path(doc.metadata_path)
            
            if file_path.exists():
                file_path.unlink()
            
            if metadata_path.exists():
                metadata_path.unlink()
            
            # Also delete from processed directory
            processed_file = self.processed_dir / f"{doc_id}_processed.json"
            if processed_file.exists():
                processed_file.unlink()
            
            return True
            
        except Exception as e:
            raise StorageError(f"Failed to delete document {doc_id}: {str(e)}")
    
    def get_file_data(self, doc_id: str) -> Optional[bytes]:
        """Get raw file data for document."""
        try:
            doc = self.get_document(doc_id)
            if not doc:
                return None
            
            file_path = Path(doc.file_path)
            if not file_path.exists():
                return None
            
            return file_path.read_bytes()
            
        except Exception as e:
            raise StorageError(f"Failed to read file data for {doc_id}: {str(e)}")
    
    def store_processed_document(self, doc_id: str, parsed_doc: ParsedDocument) -> str:
        """Store processed document data."""
        try:
            processed_filename = f"{doc_id}_processed.json"
            processed_path = self.processed_dir / processed_filename
            
            # Convert to serializable format
            processed_data = {
                'doc_id': doc_id,
                'content': parsed_doc.content,
                'pages': parsed_doc.pages,
                'images': parsed_doc.images or [],
                'tables': parsed_doc.tables or [],
                'confidence_score': parsed_doc.confidence_score,
                'parsing_method': parsed_doc.parsing_method,
                'processed_timestamp': datetime.now().isoformat(),
                'metadata': asdict(parsed_doc.metadata)
            }
            
            with open(processed_path, 'w', encoding='utf-8') as f:
                json.dump(processed_data, f, indent=2, ensure_ascii=False, default=str)
            
            # Update document status
            self.update_document_status(doc_id, "completed")
            
            return str(processed_path)
            
        except Exception as e:
            raise StorageError(f"Failed to store processed document {doc_id}: {str(e)}")
    
    def get_processed_document(self, doc_id: str) -> Optional[Dict]:
        """Get processed document data."""
        try:
            processed_path = self.processed_dir / f"{doc_id}_processed.json"
            if not processed_path.exists():
                return None
            
            with open(processed_path, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            raise StorageError(f"Failed to get processed document {doc_id}: {str(e)}")
    
    def update_document_status(self, doc_id: str, status: str) -> bool:
        """Update document processing status."""
        try:
            doc = self.get_document(doc_id)
            if not doc:
                return False
            
            doc.processing_status = status
            self._save_metadata(doc)
            
            return True
            
        except Exception as e:
            raise StorageError(f"Failed to update status for {doc_id}: {str(e)}")
    
    def get_storage_stats(self) -> Dict:
        """Get storage statistics."""
        try:
            documents = self.list_documents()
            
            total_size = sum(doc.file_size for doc in documents)
            status_counts = {}
            
            for doc in documents:
                status = doc.processing_status
                status_counts[status] = status_counts.get(status, 0) + 1
            
            return {
                'total_documents': len(documents),
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'status_counts': status_counts,
                'oldest_document': min(documents, key=lambda x: x.upload_timestamp).upload_timestamp if documents else None,
                'newest_document': max(documents, key=lambda x: x.upload_timestamp).upload_timestamp if documents else None
            }
            
        except Exception as e:
            raise StorageError(f"Failed to get storage stats: {str(e)}")
    
    def cleanup_old_files(self, days_old: int = 30) -> int:
        """Clean up files older than specified days."""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            deleted_count = 0
            
            documents = self.list_documents()
            for doc in documents:
                if doc.upload_timestamp < cutoff_date:
                    if self.delete_document(doc.doc_id):
                        deleted_count += 1
            
            return deleted_count
            
        except Exception as e:
            raise StorageError(f"Failed to cleanup old files: {str(e)}")
    
    def _save_metadata(self, stored_doc: StoredDocument):
        """Save document metadata to JSON file."""
        metadata_dict = {
            'doc_id': stored_doc.doc_id,
            'original_filename': stored_doc.original_filename,
            'stored_filename': stored_doc.stored_filename,
            'file_path': stored_doc.file_path,
            'metadata_path': stored_doc.metadata_path,
            'upload_timestamp': stored_doc.upload_timestamp.isoformat(),
            'file_size': stored_doc.file_size,
            'file_hash': stored_doc.file_hash,
            'processing_status': stored_doc.processing_status,
            'metadata': asdict(stored_doc.metadata)
        }
        
        with open(stored_doc.metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata_dict, f, indent=2, ensure_ascii=False, default=str)
    
    def _load_metadata(self, metadata_path: Path) -> StoredDocument:
        """Load document metadata from JSON file."""
        with open(metadata_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Parse datetime
        upload_timestamp = datetime.fromisoformat(data['upload_timestamp'])
        
        # Reconstruct metadata object
        metadata_dict = data['metadata']
        
        # Parse dates in metadata
        for date_field in ['created_date', 'modified_date']:
            if metadata_dict.get(date_field):
                metadata_dict[date_field] = datetime.fromisoformat(metadata_dict[date_field])
        
        metadata = DocumentMetadata(**metadata_dict)
        
        return StoredDocument(
            doc_id=data['doc_id'],
            original_filename=data['original_filename'],
            stored_filename=data['stored_filename'],
            file_path=data['file_path'],
            metadata_path=data['metadata_path'],
            upload_timestamp=upload_timestamp,
            file_size=data['file_size'],
            file_hash=data['file_hash'],
            metadata=metadata,
            processing_status=data.get('processing_status', 'uploaded')
        )
    
    def _find_by_hash(self, file_hash: str) -> Optional[StoredDocument]:
        """Find document by file hash (for deduplication)."""
        documents = self.list_documents()
        for doc in documents:
            if doc.file_hash == file_hash:
                return doc
        return None
    
    def _create_basic_metadata(self, filename: str, file_data: bytes) -> DocumentMetadata:
        """Create basic metadata when parsing is not available."""
        file_ext = Path(filename).suffix.lower()
        
        mime_map = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.doc': 'application/msword',
            '.txt': 'text/plain'
        }
        
        return DocumentMetadata(
            filename=filename,
            file_size=len(file_data),
            file_type=file_ext[1:] if file_ext else 'unknown',
            mime_type=mime_map.get(file_ext, 'application/octet-stream'),
            page_count=1,
            modified_date=datetime.now()
        )


# Global storage service instance
storage_service = StorageService()