from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class SocialAccount(Base):
    __tablename__ = "social_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Platform
    platform = Column(String, nullable=False)  # facebook, twitter, linkedin
    platform_user_id = Column(String, nullable=False)
    platform_username = Column(String)
    
    # OAuth tokens
    access_token = Column(String, nullable=False)
    refresh_token = Column(String)
    token_expires_at = Column(DateTime(timezone=True))
    
    # Profile data
    profile_data = Column(JSON, default={})
    
    # Status
    is_active = Column(Boolean, default=True)
    last_synced_at = Column(DateTime(timezone=True))
    
    # Timestamps
    connected_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="social_accounts")
