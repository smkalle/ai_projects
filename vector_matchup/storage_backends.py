"""
Storage backend implementations for the Custom RAG System
"""
import os
import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
import faiss
from loguru import logger

try:
    import lancedb
    LANCEDB_AVAILABLE = True
except ImportError:
    LANCEDB_AVAILABLE = False
    logger.warning("LanceDB not available. Install with: pip install lancedb")

from config import (
    LANCEDB_DIR, FAISS_INDEX_PATH, PARQUET_PATH, 
    TOP_K_INITIAL, ensure_data_dir
)


class StorageBackend(ABC):
    """Abstract base class for storage backends"""
    
    def __init__(self, embedding_model):
        self.embedding_model = embedding_model
        self.is_ready = False
        ensure_data_dir()
    
    @abstractmethod
    def build_index(self, chunks: List[str], metadata: Optional[List[Dict]] = None) -> bool:
        """Build the index from text chunks and optional metadata"""
        pass
    
    @abstractmethod
    def search(self, query: str, top_k: int = TOP_K_INITIAL) -> List[Dict[str, Any]]:
        """Search the index for a query"""
        pass
    
    @abstractmethod
    def is_index_ready(self) -> bool:
        """Check if the index is ready for queries"""
        pass
    
    @abstractmethod
    def get_index_info(self) -> Dict[str, Any]:
        """Get information about the current index"""
        pass


class LanceDBBackend(StorageBackend):
    """LanceDB storage and search implementation"""
    
    def __init__(self, embedding_model):
        if not LANCEDB_AVAILABLE:
            raise ImportError("LanceDB not available. Install with: pip install lancedb")
        
        super().__init__(embedding_model)
        self.db_path = LANCEDB_DIR
        self.table_name = "documents"
        self.db = None
        self.table = None
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialize LanceDB connection"""
        try:
            self.db = lancedb.connect(self.db_path)
            self._load_existing_table()
            logger.info(f"LanceDB initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize LanceDB: {e}")
            raise
    
    def _load_existing_table(self):
        """Load existing table if it exists"""
        try:
            if self.table_name in self.db.table_names():
                self.table = self.db.open_table(self.table_name)
                self.is_ready = True
                logger.info(f"Loaded existing LanceDB table '{self.table_name}'")
        except Exception as e:
            logger.warning(f"Could not load existing table: {e}")
    
    def build_index(self, chunks: List[str], metadata: Optional[List[Dict]] = None) -> bool:
        """Build LanceDB index from chunks"""
        logger.info("Building LanceDB index...")
        start_time = time.time()
        
        try:
            if not chunks:
                logger.error("No chunks provided for indexing")
                return False
            
            # Drop existing table if it exists
            if self.table_name in self.db.table_names():
                self.db.drop_table(self.table_name)
                logger.info("Dropped existing LanceDB table")
            
            # Generate embeddings
            logger.info(f"Generating embeddings for {len(chunks)} chunks...")
            embeddings = self.embedding_model.encode(
                chunks, 
                show_progress_bar=True,
                convert_to_numpy=True
            )
            
            # Prepare data for LanceDB
            data = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                doc_data = {
                    "id": i,
                    "text": chunk,
                    "vector": embedding.tolist(),
                    "chunk_index": i,
                    "char_count": len(chunk)
                }
                
                # Add metadata if provided
                if metadata and i < len(metadata):
                    doc_data.update(metadata[i])
                
                data.append(doc_data)
            
            # Create table
            self.table = self.db.create_table(self.table_name, data=data)
            self.is_ready = True
            
            build_time = time.time() - start_time
            logger.success(f"LanceDB index built successfully in {build_time:.2f} seconds")
            logger.info(f"Indexed {len(chunks)} chunks with {embeddings.shape[1]}-dimensional vectors")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to build LanceDB index: {e}")
            return False
    
    def search(self, query: str, top_k: int = TOP_K_INITIAL) -> List[Dict[str, Any]]:
        """Search LanceDB index"""
        if not self.is_ready or self.table is None:
            logger.error("LanceDB index not ready")
            return []
        
        try:
            # Generate query embedding
            query_vector = self.embedding_model.encode([query], convert_to_numpy=True)[0]
            
            # Perform search using correct API
            results = self.table.search(query_vector).limit(top_k).to_pandas()
            
            # Convert to standard format
            search_results = []
            for idx, row in results.iterrows():
                search_results.append({
                    "id": int(row["id"]),
                    "text": row["text"],
                    "score": 1.0 - float(row["_distance"]),  # Convert distance to similarity
                    "chunk_index": int(row["chunk_index"]),
                    "char_count": int(row["char_count"]),
                    "backend": "lancedb"
                })
            
            logger.info(f"LanceDB search returned {len(search_results)} results")
            return search_results
            
        except Exception as e:
            logger.error(f"LanceDB search failed: {e}")
            return []
    
    def is_index_ready(self) -> bool:
        """Check if LanceDB index is ready"""
        return self.is_ready and self.table is not None
    
    def get_index_info(self) -> Dict[str, Any]:
        """Get LanceDB index information"""
        if not self.is_ready:
            return {"status": "not_ready", "backend": "lancedb"}
        
        try:
            # Use __len__ instead of count_rows() for compatibility
            count = len(self.table)
            return {
                "status": "ready",
                "backend": "lancedb",
                "document_count": count,
                "table_name": self.table_name,
                "db_path": self.db_path
            }
        except Exception as e:
            logger.error(f"Failed to get LanceDB info: {e}")
            return {"status": "error", "backend": "lancedb", "error": str(e)}


class ParquetFAISSBackend(StorageBackend):
    """Parquet + FAISS storage and search implementation"""
    
    def __init__(self, embedding_model):
        super().__init__(embedding_model)
        self.faiss_index = None
        self.document_df = None
        self._load_existing_index()
    
    def _load_existing_index(self):
        """Load existing FAISS index and Parquet data if available"""
        try:
            if os.path.exists(FAISS_INDEX_PATH) and os.path.exists(PARQUET_PATH):
                self.faiss_index = faiss.read_index(FAISS_INDEX_PATH)
                self.document_df = pd.read_parquet(PARQUET_PATH)
                self.is_ready = True
                logger.info("Loaded existing Parquet+FAISS index")
        except Exception as e:
            logger.warning(f"Could not load existing Parquet+FAISS index: {e}")
    
    def build_index(self, chunks: List[str], metadata: Optional[List[Dict]] = None) -> bool:
        """Build Parquet+FAISS index from chunks"""
        logger.info("Building Parquet+FAISS index...")
        start_time = time.time()
        
        try:
            if not chunks:
                logger.error("No chunks provided for indexing")
                return False
            
            # Generate embeddings
            logger.info(f"Generating embeddings for {len(chunks)} chunks...")
            embeddings = self.embedding_model.encode(
                chunks,
                show_progress_bar=True,
                convert_to_numpy=True
            )
            
            # Create DataFrame for document storage
            doc_data = {
                "id": list(range(len(chunks))),
                "text": chunks,
                "chunk_index": list(range(len(chunks))),
                "char_count": [len(chunk) for chunk in chunks]
            }
            
            # Add metadata if provided
            if metadata:
                for i, meta in enumerate(metadata):
                    if i < len(chunks):
                        for key, value in meta.items():
                            if key not in doc_data:
                                doc_data[key] = [None] * len(chunks)
                            doc_data[key][i] = value
            
            self.document_df = pd.DataFrame(doc_data)
            
            # Save to Parquet
            self.document_df.to_parquet(PARQUET_PATH, index=False)
            logger.info(f"Saved {len(chunks)} documents to Parquet")
            
            # Create FAISS index
            dimension = embeddings.shape[1]
            self.faiss_index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings)
            self.faiss_index.add(embeddings)
            
            # Save FAISS index
            faiss.write_index(self.faiss_index, FAISS_INDEX_PATH)
            logger.info(f"Created FAISS index with {self.faiss_index.ntotal} vectors")
            
            self.is_ready = True
            build_time = time.time() - start_time
            logger.success(f"Parquet+FAISS index built successfully in {build_time:.2f} seconds")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to build Parquet+FAISS index: {e}")
            return False
    
    def search(self, query: str, top_k: int = TOP_K_INITIAL) -> List[Dict[str, Any]]:
        """Search Parquet+FAISS index"""
        if not self.is_ready or self.faiss_index is None or self.document_df is None:
            logger.error("Parquet+FAISS index not ready")
            return []
        
        try:
            # Generate and normalize query embedding
            query_vector = self.embedding_model.encode([query], convert_to_numpy=True)
            faiss.normalize_L2(query_vector)
            
            # Perform FAISS search
            scores, indices = self.faiss_index.search(query_vector, top_k)
            
            # Retrieve documents from Parquet
            search_results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx >= 0:  # Valid index
                    doc_row = self.document_df.iloc[idx]
                    search_results.append({
                        "id": int(doc_row["id"]),
                        "text": doc_row["text"],
                        "score": float(score),
                        "chunk_index": int(doc_row["chunk_index"]),
                        "char_count": int(doc_row["char_count"]),
                        "backend": "parquet_faiss"
                    })
            
            logger.info(f"Parquet+FAISS search returned {len(search_results)} results")
            return search_results
            
        except Exception as e:
            logger.error(f"Parquet+FAISS search failed: {e}")
            return []
    
    def is_index_ready(self) -> bool:
        """Check if Parquet+FAISS index is ready"""
        return (self.is_ready and 
                self.faiss_index is not None and 
                self.document_df is not None)
    
    def get_index_info(self) -> Dict[str, Any]:
        """Get Parquet+FAISS index information"""
        if not self.is_ready:
            return {"status": "not_ready", "backend": "parquet_faiss"}
        
        try:
            return {
                "status": "ready",
                "backend": "parquet_faiss",
                "document_count": len(self.document_df) if self.document_df is not None else 0,
                "vector_count": self.faiss_index.ntotal if self.faiss_index is not None else 0,
                "faiss_index_path": FAISS_INDEX_PATH,
                "parquet_path": PARQUET_PATH
            }
        except Exception as e:
            logger.error(f"Failed to get Parquet+FAISS info: {e}")
            return {"status": "error", "backend": "parquet_faiss", "error": str(e)}


def create_backend(backend_type: str, embedding_model) -> StorageBackend:
    """Factory function to create storage backend"""
    if backend_type.lower() == "lancedb":
        return LanceDBBackend(embedding_model)
    elif backend_type.lower() in ["parquet_faiss", "parquet", "faiss"]:
        return ParquetFAISSBackend(embedding_model)
    else:
        raise ValueError(f"Unknown backend type: {backend_type}") 