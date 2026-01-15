from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List
from models.chat import SessionState, SenderType


class ClientInfoCreate(BaseModel):
    """Schema for creating client information."""
    company_id: int = Field(..., gt=0)
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=50)


class ClientInfoResponse(BaseModel):
    """Schema for client information response."""
    id: int
    name: str
    email: str
    phone: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class SessionCreate(BaseModel):
    """Schema for creating a new chat session."""
    client_info: ClientInfoCreate


class SessionResponse(BaseModel):
    """Schema for chat session response."""
    id: int
    session_id: str
    state: SessionState
    client_info: ClientInfoResponse
    assigned_admin_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    """Schema for creating a message."""
    content: str = Field(..., min_length=1)


class MessageResponse(BaseModel):
    """Schema for message response."""
    id: int
    sender_type: SenderType
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class WebSocketMessage(BaseModel):
    """Schema for WebSocket messages."""
    type: str  # "message", "handoff_request", "session_claimed", "session_closed", etc.
    content: Optional[str] = None
    sender_type: Optional[SenderType] = None
    session_id: Optional[str] = None
    metadata: Optional[dict] = None


class AdminResponse(BaseModel):
    """Schema for admin user response."""
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class AdminLogin(BaseModel):
    """Schema for admin login."""
    username: str
    password: str


class AdminRegister(BaseModel):
    """Schema for admin registration."""
    company_id: int = Field(..., gt=0)
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    role: Optional[str] = "AGENT"  # AGENT or COMPANY_ADMIN


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token payload data."""
    username: Optional[str] = None
    exp: Optional[datetime] = None
