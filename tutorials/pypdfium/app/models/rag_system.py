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

        self.qdrant_client = QdrantClient(qdrant_url, port=qdrant_port)
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=openai_api_key,
            model="text-embedding-3-small"
        )
        self.collection_name = collection_name
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )

    def ensure_collection_exists(self):
        """Create collection if it doesn't exist"""
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
        try:
            # Ensure collection exists
            self.ensure_collection_exists()

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
