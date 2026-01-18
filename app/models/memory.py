from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Memory(Base):
    __tablename__ = "memories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Content
    content = Column(Text, nullable=False)
    source = Column(String, nullable=False)  # twitter, linkedin, facebook, manual
    category = Column(String)  # preferences, facts, events, etc.
    
    # Metadata (using meta_data to avoid SQLAlchemy reserved attribute)
    meta_data = Column(JSON, default={}, name="metadata")
    original_post_id = Column(String)  # ID from social media platform
    original_url = Column(String)
    
    # Vector search
    vector_id = Column(String, unique=True)  # ID in Qdrant
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    source_timestamp = Column(DateTime(timezone=True))  # When was it posted originally
    
    # Relationships
    user = relationship("User", back_populates="memories")
