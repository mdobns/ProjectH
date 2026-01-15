from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .database import Base


class SuperAdminRole(str, enum.Enum):
    """Super admin roles."""
    SUPER_ADMIN = "SUPER_ADMIN"


class SuperAdmin(Base):
    """Super admin model for platform management."""
    __tablename__ = "super_admins"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(Enum(SuperAdminRole), default=SuperAdminRole.SUPER_ADMIN, nullable=False)
    is_active = Column(Integer, default=1)  # Using Integer for SQLite compatibility
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
