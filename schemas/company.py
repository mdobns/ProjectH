from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime


class CompanyBase(BaseModel):
    """Base company schema."""
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=50)
    website: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None


class CompanyCreate(CompanyBase):
    """Schema for creating a company."""
    slug: str = Field(..., min_length=2, max_length=100, pattern="^[a-z0-9-]+$")
    password: str = Field(..., min_length=8)
    
    @validator('slug')
    def slug_must_be_lowercase(cls, v):
        return v.lower()


class CompanyUpdate(BaseModel):
    """Schema for updating company information."""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    website: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    logo_url: Optional[str] = Field(None, max_length=500)


class CompanyResponse(CompanyBase):
    """Schema for company response."""
    id: int
    slug: str
    logo_url: Optional[str] = None
    subscription_plan: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CompanyLoginRequest(BaseModel):
    """Schema for company login."""
    slug: str
    password: str


class CompanyStats(BaseModel):
    """Schema for company statistics."""
    total_resources: int = 0
    total_agents: int = 0
    total_sessions: int = 0
    active_sessions: int = 0
    total_messages: int = 0
