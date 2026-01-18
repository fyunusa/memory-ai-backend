from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Permission(Base):
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # App requesting access
    app_name = Column(String, nullable=False)
    app_id = Column(String, nullable=False, index=True)
    
    # Permissions granted
    scopes = Column(JSON, default=[])  # List of data categories allowed
    
    # Access control
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime(timezone=True))  # Time-limited access
    
    # Usage tracking
    last_accessed_at = Column(DateTime(timezone=True))
    access_count = Column(Integer, default=0)
    
    # Timestamps
    granted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="permissions")
