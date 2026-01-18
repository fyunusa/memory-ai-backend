from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict, Optional
from uuid import uuid4
from app.config import settings
from app.services.embedding_service import embedding_service
from app.database import SessionLocal
from app.models.memory import Memory
from datetime import datetime


class MemoryService:
    """Service for managing memories in PostgreSQL and Qdrant"""
    
    def __init__(self):
        self.qdrant_client = QdrantClient(url=settings.QDRANT_URL)
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        self._ensure_collection_exists()
    
    def _ensure_collection_exists(self):
        """Create Qdrant collection if it doesn't exist"""
        try:
            collections = self.qdrant_client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if self.collection_name not in collection_names:
                dimension = embedding_service.get_embedding_dimension()
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=dimension, distance=Distance.COSINE)
                )
                print(f"Created Qdrant collection: {self.collection_name}")
        except Exception as e:
            print(f"Error ensuring collection exists: {str(e)}")
    
    def create_memory(
        self,
        user_id: int,
        content: str,
        source: str,
        category: Optional[str] = None,
        meta_data: Optional[Dict] = None,
        original_post_id: Optional[str] = None,
        original_url: Optional[str] = None,
        source_timestamp: Optional[datetime] = None,
        generate_embedding: bool = False
    ) -> Dict:
        """Create a new memory (embeddings optional)"""
        try:
            db = SessionLocal()
            
            vector_id = None
            
            # Only generate embedding if requested AND API key is configured
            if generate_embedding:
                api_key = settings.COHERE_API_KEY if settings.EMBEDDING_PROVIDER == "cohere" else settings.OPENAI_API_KEY
                if api_key and not api_key.startswith("your-"):
                    try:
                        embedding = embedding_service.generate_embedding(content)
                        vector_id = str(uuid4())
                        
                        # Store in Qdrant
                        self.qdrant_client.upsert(
                            collection_name=self.collection_name,
                            points=[
                                PointStruct(
                                    id=vector_id,
                                    vector=embedding,
                                    payload={
                                        "user_id": user_id,
                                        "content": content,
                                        "source": source,
                                        "category": category,
                                        "original_post_id": original_post_id,
                                        "original_url": original_url
                                    }
                                )
                            ]
                        )
                    except Exception as e:
                        print(f"Embedding generation skipped: {str(e)}")
            
            # Store in PostgreSQL (always happens)
            memory = Memory(
                user_id=user_id,
                content=content,
                source=source,
                category=category or "general",
                meta_data=meta_data or {},
                original_post_id=original_post_id,
                original_url=original_url,
                vector_id=vector_id,
                source_timestamp=source_timestamp or datetime.utcnow()
            )
            
            db.add(memory)
            db.commit()
            db.refresh(memory)
            
            return {
                "success": True,
                "memory_id": memory.id,
                "vector_id": vector_id,
                "embedding_generated": vector_id is not None,
                "content_preview": content[:100] + "..." if len(content) > 100 else content
            }
        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}
        finally:
            db.close()
    
    def search_memories(
        self,
        query: str,
        user_id: Optional[int] = None,
        limit: int = 10,
        source_filter: Optional[str] = None
    ) -> Dict:
        """Semantic search for memories"""
        try:
            # Generate query embedding
            query_embedding = embedding_service.generate_embedding(query)
            
            # Build filter
            search_filter = None
            if user_id or source_filter:
                must_conditions = []
                if user_id:
                    must_conditions.append({"key": "user_id", "match": {"value": user_id}})
                if source_filter:
                    must_conditions.append({"key": "source", "match": {"value": source_filter}})
                
                search_filter = {"must": must_conditions}
            
            # Search in Qdrant
            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=search_filter,
                limit=limit
            )
            
            # Format results
            memories = []
            for result in search_results:
                memories.append({
                    "id": result.id,
                    "score": result.score,
                    "content": result.payload.get("content", ""),
                    "source": result.payload.get("source", ""),
                    "category": result.payload.get("category", ""),
                    "original_url": result.payload.get("original_url")
                })
            
            return {
                "success": True,
                "query": query,
                "count": len(memories),
                "results": memories
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_memory_by_id(self, memory_id: int, user_id: Optional[int] = None) -> Dict:
        """Get a specific memory by ID"""
        try:
            db = SessionLocal()
            query = db.query(Memory).filter(Memory.id == memory_id)
            
            if user_id:
                query = query.filter(Memory.user_id == user_id)
            
            memory = query.first()
            
            if not memory:
                return {"success": False, "error": "Memory not found"}
            
            return {
                "success": True,
                "memory": {
                    "id": memory.id,
                    "content": memory.content,
                    "source": memory.source,
                    "category": memory.category,
                    "created_at": memory.created_at.isoformat(),
                    "source_timestamp": memory.source_timestamp.isoformat() if memory.source_timestamp else None,
                    "original_url": memory.original_url,
                    "meta_data": memory.meta_data
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            db.close()
    
    def list_memories(
        self,
        user_id: int,
        source: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict:
        """List memories for a user"""
        try:
            db = SessionLocal()
            query = db.query(Memory).filter(Memory.user_id == user_id)
            
            if source:
                query = query.filter(Memory.source == source)
            
            total = query.count()
            memories = query.order_by(Memory.created_at.desc()).limit(limit).offset(offset).all()
            
            return {
                "success": True,
                "total": total,
                "count": len(memories),
                "memories": [
                    {
                        "id": m.id,
                        "content": m.content[:200] + "..." if len(m.content) > 200 else m.content,
                        "source": m.source,
                        "category": m.category,
                        "created_at": m.created_at.isoformat()
                    }
                    for m in memories
                ]
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            db.close()
    
    def delete_memory(self, memory_id: int, user_id: int) -> Dict:
        """Delete a memory"""
        try:
            db = SessionLocal()
            memory = db.query(Memory).filter(
                Memory.id == memory_id,
                Memory.user_id == user_id
            ).first()
            
            if not memory:
                return {"success": False, "error": "Memory not found"}
            
            # Delete from Qdrant
            if memory.vector_id:
                self.qdrant_client.delete(
                    collection_name=self.collection_name,
                    points_selector=[memory.vector_id]
                )
            
            # Delete from PostgreSQL
            db.delete(memory)
            db.commit()
            
            return {"success": True, "message": "Memory deleted"}
        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}
        finally:
            db.close()


# Singleton instance
memory_service = MemoryService()
