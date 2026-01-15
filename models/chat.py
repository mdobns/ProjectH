from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .database import Base


class SessionState(str, enum.Enum):
    """Chat session states."""
    AI = "AI"
    HUMAN = "HUMAN"
    CLOSED = "CLOSED"


class SenderType(str, enum.Enum):
    """Message sender types."""
    CLIENT = "CLIENT"
    AI = "AI"
    ADMIN = "ADMIN"


class ClientInfo(Base):
    """Client information model."""
    __tablename__ = "client_info"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="client_info")
    sessions = relationship("ChatSession", back_populates="client_info")


class ChatSession(Base):
    """Chat session model."""
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    state = Column(Enum(SessionState), default=SessionState.AI, nullable=False)
    client_info_id = Column(Integer, ForeignKey("client_info.id"), nullable=False)
    assigned_admin_id = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)
    
    # Relationships
    company = relationship("Company", back_populates="chat_sessions")
    client_info = relationship("ClientInfo", back_populates="sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")
    assigned_admin = relationship("AdminUser", back_populates="sessions")


class Message(Base):
    """Message model."""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    sender_type = Column(Enum(SenderType), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    session = relationship("ChatSession", back_populates="messages")


class AdminRole(str, enum.Enum):
    """Admin user roles."""
    AGENT = "AGENT"  # Customer support agent
    COMPANY_ADMIN = "COMPANY_ADMIN"  # Company administrator


class AdminUser(Base):
    """Admin user model."""
    __tablename__ = "admin_users"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(Enum(AdminRole), default=AdminRole.AGENT, nullable=False)
    is_active = Column(Integer, default=1)  # Using Integer for SQLite compatibility
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="admin_users")
    sessions = relationship("ChatSession", back_populates="assigned_admin")
