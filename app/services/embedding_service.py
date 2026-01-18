from openai import OpenAI
import cohere
from typing import List, Dict
from app.config import settings


class EmbeddingService:
    """Service for generating embeddings using OpenAI or Cohere"""
    
    def __init__(self):
        self.provider = settings.EMBEDDING_PROVIDER
        
        if self.provider == "openai":
            self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = settings.EMBEDDING_MODEL
        elif self.provider == "cohere":
            self.cohere_client = cohere.Client(settings.COHERE_API_KEY)
            self.model = settings.COHERE_EMBEDDING_MODEL
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        try:
            if self.provider == "openai":
                response = self.openai_client.embeddings.create(
                    input=text,
                    model=self.model
                )
                return response.data[0].embedding
            
            elif self.provider == "cohere":
                response = self.cohere_client.embed(
                    texts=[text],
                    model=self.model,
                    input_type="search_document"
                )
                return response.embeddings[0]
            
            else:
                raise Exception(f"Unknown embedding provider: {self.provider}")
        except Exception as e:
            raise Exception(f"Embedding generation failed: {str(e)}")
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        try:
            if self.provider == "openai":
                response = self.openai_client.embeddings.create(
                    input=texts,
                    model=self.model
                )
                return [item.embedding for item in response.data]
            
            elif self.provider == "cohere":
                response = self.cohere_client.embed(
                    texts=texts,
                    model=self.model,
                    input_type="search_document"
                )
                return response.embeddings
            
            else:
                raise Exception(f"Unknown embedding provider: {self.provider}")
        except Exception as e:
            raise Exception(f"Batch embedding generation failed: {str(e)}")
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings for this model"""
        if self.provider == "openai":
            if "text-embedding-3-small" in self.model:
                return 1536
            elif "text-embedding-3-large" in self.model:
                return 3072
            elif "text-embedding-ada-002" in self.model:
                return 1536
            return 1536
        
        elif self.provider == "cohere":
            # Cohere embed-english-v3.0 produces 1024-dimensional vectors
            if "embed-english-v3.0" in self.model:
                return 1024
            elif "embed-multilingual-v3.0" in self.model:
                return 1024
            return 1024
        
        return 1536  # default


# Singleton instance
embedding_service = EmbeddingService()
