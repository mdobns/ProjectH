from pydantic import BaseModel, HttpUrl, Field
from typing import Optional
from datetime import datetime


class ResourceBase(BaseModel):
    """Base resource schema."""
    resource_type: str  # PDF, WEBSITE, FACEBOOK, TEXT


class ResourceCreate(BaseModel):
    """Schema for creating a resource."""
    resource_type: str = Field(..., pattern="^(PDF|WEBSITE|FACEBOOK|TEXT)$")
    source_url: Optional[str] = Field(None, max_length=1000)
    text_content: Optional[str] = None  # For TEXT type
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "resource_type": "WEBSITE",
                    "source_url": "https://example.com"
                },
                {
                    "resource_type": "FACEBOOK",
                    "source_url": "https://facebook.com/yourpage"
                },
                {
                    "resource_type": "TEXT",
                    "text_content": "Custom knowledge base text content"
                }
            ]
        }


class ResourceUpdate(BaseModel):
    """Schema for updating resource information."""
    is_active: Optional[bool] = None


class ResourceResponse(BaseModel):
    """Schema for resource response."""
    id: int
    company_id: int
    resource_type: str
    source_url: Optional[str] = None
    file_name: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ResourceListResponse(BaseModel):
    """Schema for resource list response."""
    resources: list[ResourceResponse]
    total: int
    page: int
    page_size: int


class ResourceContentResponse(BaseModel):
    """Schema for resource content response (for preview)."""
    id: int
    resource_type: str
    file_name: Optional[str] = None
    source_url: Optional[str] = None
    content_preview: str  # First 500 chars
    total_length: int
    status: str
    
    class Config:
        from_attributes = True
