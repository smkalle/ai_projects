"""
RAG System for Energy Document AI
Handles vector storage, embeddings, and retrieval using Qdrant
"""

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
import uuid
from typing import List, Dict, Optional, Tuple
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class EnergyRAGSystem:
    """RAG system optimized for energy sector documents"""

    def __init__(self, 
                 qdrant_url: str = "localhost", 
                 qdrant_port: int = 6333,
                 openai_api_key: str = None,
                 collection_name: str = "energy_documents"):

        self.qdrant_url = qdrant_url
        self.qdrant_port = qdrant_port
        self.collection_name = collection_name
        self.qdrant_available = False
        self.qdrant_client = None
        
        # Initialize embeddings if API key available
        self.embeddings = None
        if openai_api_key:
            try:
                self.embeddings = OpenAIEmbeddings(
                    openai_api_key=openai_api_key,
                    model="text-embedding-3-small"
                )
            except Exception as e:
                logger.warning(f"Failed to initialize embeddings: {e}")
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
        
        # Try to connect to Qdrant
        self._initialize_qdrant()

    def _initialize_qdrant(self):
        """Initialize Qdrant connection with graceful fallback"""
        try:
            self.qdrant_client = QdrantClient(self.qdrant_url, port=self.qdrant_port)
            # Test connection
            collections = self.qdrant_client.get_collections()
            self.qdrant_available = True
            logger.info(f"Successfully connected to Qdrant at {self.qdrant_url}:{self.qdrant_port}")
        except Exception as e:
            self.qdrant_available = False
            self.qdrant_client = None
            logger.warning(f"Qdrant not available at {self.qdrant_url}:{self.qdrant_port}: {e}")
            logger.info("System will continue without vector storage capabilities")

    def is_available(self) -> bool:
        """Check if RAG system is fully available"""
        return self.qdrant_available and self.embeddings is not None

    def get_status(self) -> dict:
        """Get system status information"""
        return {
            "qdrant_available": self.qdrant_available,
            "qdrant_url": f"{self.qdrant_url}:{self.qdrant_port}",
            "embeddings_available": self.embeddings is not None,
            "collection_name": self.collection_name,
            "fully_operational": self.is_available()
        }

    def ensure_collection_exists(self):
        """Create collection if it doesn't exist"""
        if not self.qdrant_available:
            logger.warning("Qdrant not available, cannot create collection")
            return False
            
        try:
            collections = self.qdrant_client.get_collections()
            collection_names = [col.name for col in collections.collections]

            if self.collection_name not in collection_names:
                # Get embedding dimension
                sample_embedding = self.embeddings.embed_query("sample text")

                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=len(sample_embedding), 
                        distance=Distance.COSINE
                    ),
                )
                logger.info(f"Created collection: {self.collection_name}")
            else:
                logger.info(f"Collection {self.collection_name} already exists")

        except Exception as e:
            logger.error(f"Error ensuring collection exists: {e}")
            raise

    def process_and_store_document(self, 
                                   text: str, 
                                   document_name: str,
                                   document_type: str = "energy",
                                   metadata: Dict = None) -> int:
        """Process document text and store in vector database"""
        if not self.is_available():
            logger.warning("RAG system not fully available (Qdrant or embeddings missing)")
            # Still split text for consistency, but don't store
            chunks = self.text_splitter.split_text(text)
            return len(chunks)  # Return number of chunks that would have been stored
            
        try:
            # Ensure collection exists
            if not self.ensure_collection_exists():
                return 0

            # Split text into chunks
            chunks = self.text_splitter.split_text(text)
            logger.info(f"Split document into {len(chunks)} chunks")

            # Generate embeddings
            embeddings_list = self.embeddings.embed_documents(chunks)

            # Prepare points for insertion
            points = []
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings_list)):
                point_id = str(uuid.uuid4())

                # Prepare metadata
                point_metadata = {
                    "document_name": document_name,
                    "document_type": document_type,
                    "chunk_index": i,
                    "chunk_text": chunk,
                    "timestamp": datetime.now().isoformat(),
                    "text_length": len(chunk)
                }

                # Add additional metadata if provided
                if metadata:
                    point_metadata.update(metadata)

                points.append(PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=point_metadata
                ))

            # Insert into Qdrant
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=points
            )

            logger.info(f"Stored {len(points)} chunks from {document_name}")
            return len(points)

        except Exception as e:
            logger.error(f"Error processing document {document_name}: {e}")
            raise

    def similarity_search(self, 
                         query: str, 
                         k: int = 5,
                         document_type: Optional[str] = None,
                         score_threshold: float = 0.7) -> List[Dict]:
        """Perform similarity search with optional filtering"""
        if not self.is_available():
            logger.warning("RAG system not available, cannot perform similarity search")
            return []  # Return empty results
            
        try:
            # Generate query embedding
            query_embedding = self.embeddings.embed_query(query)

            # Prepare filter if document type specified
            query_filter = None
            if document_type:
                query_filter = Filter(
                    must=[
                        FieldCondition(
                            key="document_type",
                            match=MatchValue(value=document_type)
                        )
                    ]
                )

            # Search in Qdrant
            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=query_filter,
                limit=k,
                score_threshold=score_threshold
            )

            # Format results
            results = []
            for hit in search_results:
                result = {
                    "content": hit.payload["chunk_text"],
                    "score": hit.score,
                    "document_name": hit.payload["document_name"],
                    "document_type": hit.payload["document_type"],
                    "chunk_index": hit.payload["chunk_index"],
                    "metadata": hit.payload
                }
                results.append(result)

            logger.info(f"Found {len(results)} relevant chunks for query")
            return results

        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            return []

    def get_document_stats(self) -> Dict:
        """Get statistics about stored documents"""
        if not self.qdrant_available:
            return {
                "total_points": 0,
                "total_documents": 0,
                "document_types": {},
                "collection_status": "qdrant_unavailable"
            }
            
        try:
            collection_info = self.qdrant_client.get_collection(self.collection_name)

            # Get document counts by type
            scroll_result = self.qdrant_client.scroll(
                collection_name=self.collection_name,
                limit=1000  # Adjust based on your collection size
            )

            doc_types = {}
            doc_names = set()

            for point in scroll_result[0]:
                doc_type = point.payload.get("document_type", "unknown")
                doc_name = point.payload.get("document_name", "unknown")

                doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
                doc_names.add(doc_name)

            return {
                "total_points": collection_info.points_count,
                "total_documents": len(doc_names),
                "document_types": doc_types,
                "collection_status": collection_info.status
            }

        except Exception as e:
            logger.error(f"Error getting document stats: {e}")
            return {}
