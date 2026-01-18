from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any, List


class MemoryBase(BaseModel):
    content: str
    source: str
    category: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}


class MemoryCreate(MemoryBase):
    pass


class MemoryQuery(BaseModel):
    query: str
    limit: int = 10
    category: Optional[str] = None
    source: Optional[str] = None


class MemoryResponse(MemoryBase):
    id: int
    user_id: int
    vector_id: Optional[str]
    created_at: datetime
    source_timestamp: Optional[datetime]
    
    class Config:
        from_attributes = True


class MemoryQueryResult(BaseModel):
    memories: List[MemoryResponse]
    total: int
    query: str
