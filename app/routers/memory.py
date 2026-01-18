from fastapi import APIRouter, Query, Body
from typing import Optional
from app.services.memory_service import memory_service

router = APIRouter()


@router.post("/create")
async def create_memory(
    content: str = Body(..., description="Memory content"),
    source: str = Body(..., description="Source: twitter, linkedin, notion, file, manual"),
    user_id: int = Body(1, description="User ID (temporarily hardcoded for testing)"),
    category: Optional[str] = Body(None, description="Category tag"),
    original_url: Optional[str] = Body(None, description="Original source URL"),
    generate_embedding: bool = Body(True, description="Generate embedding with Cohere (free)")
):
    """Create a new memory with optional embedding"""
    return memory_service.create_memory(
        user_id=user_id,
        content=content,
        source=source,
        category=category,
        original_url=original_url,
        generate_embedding=generate_embedding
    )


@router.get("/search")
async def search_memories(
    query: str = Query(..., description="Search query"),
    user_id: int = Query(1, description="User ID"),
    limit: int = Query(10, ge=1, le=50),
    source: Optional[str] = Query(None, description="Filter by source")
):
    """Semantic search for memories"""
    return memory_service.search_memories(
        query=query,
        user_id=user_id,
        limit=limit,
        source_filter=source
    )


@router.get("/list")
async def list_memories(
    user_id: int = Query(1, description="User ID"),
    source: Optional[str] = Query(None, description="Filter by source"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """List all memories for a user"""
    return memory_service.list_memories(
        user_id=user_id,
        source=source,
        limit=limit,
        offset=offset
    )


@router.get("/{memory_id}")
async def get_memory(
    memory_id: int,
    user_id: int = Query(1, description="User ID")
):
    """Get a specific memory by ID"""
    return memory_service.get_memory_by_id(memory_id, user_id)


@router.delete("/{memory_id}")
async def delete_memory(
    memory_id: int,
    user_id: int = Query(1, description="User ID")
):
    """Delete a memory"""
    return memory_service.delete_memory(memory_id, user_id)
