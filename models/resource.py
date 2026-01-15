from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .database import Base


class ResourceType(str, enum.Enum):
    """Resource types for knowledge base."""
    PDF = "PDF"
    WEBSITE = "WEBSITE"
    FACEBOOK = "FACEBOOK"
    TEXT = "TEXT"


class ResourceStatus(str, enum.Enum):
    """Resource processing status."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Resource(Base):
    """Knowledge base resource model."""
    __tablename__ = "resources"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    resource_type = Column(Enum(ResourceType), nullable=False)
    
    # Source information
    source_url = Column(String(1000), nullable=True)  # For web/Facebook resources
    file_path = Column(String(500), nullable=True)  # For uploaded files
    file_name = Column(String(255), nullable=True)  # Original filename
    
    # Extracted content
    extracted_content = Column(Text, nullable=True)  # Text content extracted
    metadata = Column(Text, nullable=True)  # JSON string for additional info
    
    # Processing status
    status = Column(Enum(ResourceStatus), default=ResourceStatus.PENDING, nullable=False)
    error_message = Column(Text, nullable=True)  # Error details if failed
    
    # Management
    is_active = Column(Integer, default=1)  # Using Integer for SQLite compatibility
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)  # When processing completed
    
    # Relationships
    company = relationship("Company", back_populates="resources")
