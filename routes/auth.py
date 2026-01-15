from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.database import get_db
from models.chat import AdminUser
from schemas.chat import AdminLogin, AdminRegister, Token
from auth.jwt import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_password_hash,
    verify_token,
)
from datetime import timedelta
from config import settings

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register_admin(
    admin_data: AdminRegister,
    db: Session = Depends(get_db)
):
    """
    Register a new admin user.
    
    Returns JWT access and refresh tokens.
    """
    # Verify company exists
    from models import Company, AdminRole
    company = db.query(Company).filter(Company.id == admin_data.company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Check if username already exists
    existing_admin = db.query(AdminUser).filter(
        AdminUser.username == admin_data.username
    ).first()
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    existing_email = db.query(AdminUser).filter(
        AdminUser.email == admin_data.email
    ).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate role
    try:
        role = AdminRole[admin_data.role.upper()]
    except (KeyError, AttributeError):
        role = AdminRole.AGENT
    
    # Create new admin
    hashed_password = get_password_hash(admin_data.password)
    new_admin = AdminUser(
        company_id=admin_data.company_id,
        username=admin_data.username,
        email=admin_data.email,
        hashed_password=hashed_password,
        full_name=admin_data.full_name,
        role=role,
        is_active=1
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    
    # Generate tokens
    access_token = create_access_token(
        data={
            "sub": new_admin.username,
            "admin_id": new_admin.id,
            "company_id": new_admin.company_id
        }
    )
    refresh_token = create_refresh_token(
        data={
            "sub": new_admin.username,
            "admin_id": new_admin.id,
            "company_id": new_admin.company_id
        }
    )
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/login", response_model=Token)
async def login_admin(
    credentials: AdminLogin,
    db: Session = Depends(get_db)
):
    """
    Login admin user.
    
    Returns JWT access and refresh tokens.
    """
    # Find admin by username
    admin = db.query(AdminUser).filter(
        AdminUser.username == credentials.username
    ).first()
    
    if not admin or not verify_password(credentials.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account is inactive"
        )
    
    # Generate tokens
    access_token = create_access_token(
        data={
            "sub": admin.username,
            "admin_id": admin.id,
            "company_id": admin.company_id
        }
    )
    refresh_token = create_refresh_token(
        data={
            "sub": admin.username,
            "admin_id": admin.id,
            "company_id": admin.company_id
        }
    )
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/refresh", response_model=Token)
async def refresh_token_endpoint(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    """
    # Verify refresh token
    payload = verify_token(refresh_token, token_type="refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    username = payload.get("sub")
    admin_id = payload.get("admin_id")
    
    # Verify admin still exists and is active
    admin = db.query(AdminUser).filter(AdminUser.id == admin_id).first()
    if not admin or not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin not found or inactive"
        )
    
    # Generate new tokens
    new_access_token = create_access_token(
        data={"sub": username, "admin_id": admin_id}
    )
    new_refresh_token = create_refresh_token(
        data={"sub": username, "admin_id": admin_id}
    )
    
    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token
    )
