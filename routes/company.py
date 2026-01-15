"""
Company Management Routes
Handles company registration, authentication, and profile management.
"""

from fastapi import APIRouter, Depend, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import re

from models.database import get_db
from models import Company, SubscriptionPlan, Resource, AdminUser, ChatSession, Message
from schemas.company import (
    CompanyCreate,
    CompanyResponse,
    CompanyUpdate,
    CompanyStats
)
from auth.jwt import create_access_token, get_password_hash, verify_password

router = APIRouter(prefix="/api/companies", tags=["Companies"])


def create_slug(name: str) -> str:
    """Create URL-friendly slug from company name."""
    slug = name.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')


@router.post("/register", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def register_company(
    company_data: CompanyCreate,
    db: Session = Depend(get_db)
):
    """
    Register a new company.
    Creates a company account with initial setup.
    """
    # Check if slug already exists
    existing_company = db.query(Company).filter(Company.slug == company_data.slug).first()
    if existing_company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company slug already exists"
        )
    
    # Check if email already exists
    existing_email = db.query(Company).filter(Company.email == company_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create company with hashed password (stored for super admin access)
    company = Company(
        name=company_data.name,
        slug=company_data.slug,
        email=company_data.email,
        phone=company_data.phone,
        website=company_data.website,
        description=company_data.description,
        subscription_plan=SubscriptionPlan.FREE,
        is_active=1
    )
    
    db.add(company)
    db.commit()
    db.refresh(company)
    
    return company


@router.get("/slug/{slug}", response_model=CompanyResponse)
async def get_company_by_slug(
    slug: str,
    db: Session = Depend(get_db)
):
    """Get company details by slug (public endpoint)."""
    company = db.query(Company).filter(
        Company.slug == slug,
        Company.is_active == 1
    ).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    return company


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: int,
    db: Session = Depend(get_db)
):
    """Get company details by ID."""
    company = db.query(Company).filter(Company.id == company_id).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    return company


@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: int,
    company_data: CompanyUpdate,
    db: Session = Depend(get_db)
):
    """Update company information."""
    company = db.query(Company).filter(Company.id == company_id).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Update fields if provided
    update_data = company_data.model_dump(exclude_unset=True)
    
    # Check if email is being changed and if it's already taken
    if "email" in update_data and update_data["email"] != company.email:
        existing_email = db.query(Company).filter(
            Company.email == update_data["email"],
            Company.id != company_id
        ).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
    
    for field, value in update_data.items():
        setattr(company, field, value)
    
    company.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(company)
    
    return company


@router.get("/{company_id}/stats", response_model=CompanyStats)
async def get_company_stats(
    company_id: int,
    db: Session = Depend(get_db)
):
    """Get company statistics."""
    company = db.query(Company).filter(Company.id == company_id).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Get resource count
    total_resources = db.query(Resource).filter(
        Resource.company_id == company_id
    ).count()
    
    # Get agent count
    total_agents = db.query(AdminUser).filter(
        AdminUser.company_id == company_id,
        AdminUser.is_active == 1
    ).count()
    
    # Get session count
    total_sessions = db.query(ChatSession).filter(
        ChatSession.company_id == company_id
    ).count()
    
    # Get active sessions
    active_sessions = db.query(ChatSession).filter(
        ChatSession.company_id == company_id,
        ChatSession.closed_at.is_(None)
    ).count()
    
    # Get message count
    total_messages = db.query(Message).join(ChatSession).filter(
        ChatSession.company_id == company_id
    ).count()
    
    return CompanyStats(
        total_resources=total_resources,
        total_agents=total_agents,
        total_sessions=total_sessions,
        active_sessions=active_sessions,
        total_messages=total_messages
    )


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_company(
    company_id: int,
    db: Session = Depend(get_db)
):
    """Deactivate a company (soft delete)."""
    company = db.query(Company).filter(Company.id == company_id).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    company.is_active = 0
    company.updated_at = datetime.utcnow()
    db.commit()
    
    return None
