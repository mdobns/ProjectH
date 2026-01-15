"""
Resource Management Routes
Handles resource uploads, processing, and management.
"""

from fastapi import APIRouter, Depend, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime
import os
import aiofiles
import uuid

from models.database import get_db
from models import Resource, ResourceType, ResourceStatus, Company
from schemas.resource import (
    ResourceCreate,
    ResourceResponse,
    ResourceUpdate,
    ResourceListResponse,
    ResourceContentResponse
)
from services.resource_service import ResourceService

router = APIRouter(prefix="/api/resources", tags=["Resources"])

# Create uploads directory if it doesn't exist
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


async def process_resource_task(resource_id: int, resource_type: str, file_path: str = None):
    """Background task to process resources."""
    from models.database import SessionLocal
    db = SessionLocal()
    
    try:
        resource = db.query(Resource).filter(Resource.id == resource_id).first()
        if not resource:
            return
        
        if resource_type == "PDF":
            await ResourceService.process_pdf_resource(resource, file_path, db)
        elif resource_type == "WEBSITE":
            await ResourceService.process_website_resource(resource, db)
        elif resource_type == "FACEBOOK":
            await ResourceService.process_facebook_resource(resource, db)
            
    finally:
        db.close()


@router.post("/upload-pdf", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED)
async def upload_pdf(
    company_id: int,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depend(get_db)
):
    """
    Upload a PDF file for knowledge base.
    The file will be processed in the background.
    """
    # Verify company exists
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    company_dir = os.path.join(UPLOAD_DIR, str(company_id))
    os.makedirs(company_dir, exist_ok=True)
    file_path = os.path.join(company_dir, unique_filename)
    
    # Save file
    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # Create resource entry
    resource = Resource(
        company_id=company_id,
        resource_type=ResourceType.PDF,
        file_path=file_path,
        file_name=file.filename,
        status=ResourceStatus.PENDING
    )
    
    db.add(resource)
    db.commit()
    db.refresh(resource)
    
    # Process in background
    background_tasks.add_task(process_resource_task, resource.id, "PDF", file_path)
    
    return resource


@router.post("/add-website", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED)
async def add_website(
    company_id: int,
    resource_data: ResourceCreate,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depend(get_db)
):
    """
    Add a website URL for knowledge base.
    The website will be scrapped in the background.
    """
    # Verify company exists
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    if resource_data.resource_type != "WEBSITE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resource type must be WEBSITE"
        )
    
    if not resource_data.source_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="source_url is required for website resources"
        )
    
    # Create resource entry
    resource = Resource(
        company_id=company_id,
        resource_type=ResourceType.WEBSITE,
        source_url=resource_data.source_url,
        status=ResourceStatus.PENDING
    )
    
    db.add(resource)
    db.commit()
    db.refresh(resource)
    
    # Process in background
    background_tasks.add_task(process_resource_task, resource.id, "WEBSITE")
    
    return resource


@router.post("/add-facebook", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED)
async def add_facebook_page(
    company_id: int,
    resource_data: ResourceCreate,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depend(get_db)
):
    """
    Add a Facebook page URL for knowledge base.
    The page will be scraped in the background.
    """
    # Verify company exists
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    if resource_data.resource_type != "FACEBOOK":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resource type must be FACEBOOK"
        )
    
    if not resource_data.source_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="source_url is required for Facebook resources"
        )
    
    # Create resource entry
    resource = Resource(
        company_id=company_id,
        resource_type=ResourceType.FACEBOOK,
        source_url=resource_data.source_url,
        status=ResourceStatus.PENDING
    )
    
    db.add(resource)
    db.commit()
    db.refresh(resource)
    
    # Process in background
    background_tasks.add_task(process_resource_task, resource.id, "FACEBOOK")
    
    return resource


@router.post("/add-text", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED)
async def add_text(
    company_id: int,
    resource_data: ResourceCreate,
    db: Session = Depend(get_db)
):
    """Add custom text content for knowledge base."""
    # Verify company exists
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    if resource_data.resource_type != "TEXT":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resource type must be TEXT"
        )
    
    if not resource_data.text_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="text_content is required for text resources"
        )
    
    # Create and immediately complete resource
    resource = Resource(
        company_id=company_id,
        resource_type=ResourceType.TEXT,
        extracted_content=resource_data.text_content,
        status=ResourceStatus.COMPLETED,
        processed_at=datetime.utcnow()
    )
    
    db.add(resource)
    db.commit()
    db.refresh(resource)
    
    return resource


@router.get("", response_model=ResourceListResponse)
async def list_resources(
    company_id: int,
    page: int = 1,
    page_size: int = 20,
    status_filter: str = None,
    db: Session = Depend(get_db)
):
    """List all resources for a company with pagination."""
    # Verify company exists
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    query = db.query(Resource).filter(Resource.company_id == company_id)
    
    # Apply status filter if provided
    if status_filter:
        try:
            status_enum = ResourceStatus[status_filter.upper()]
            query = query.filter(Resource.status == status_enum)
        except KeyError:
            pass
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    resources = query.order_by(Resource.created_at.desc()).offset(offset).limit(page_size).all()
    
    return ResourceListResponse(
        resources=resources,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{resource_id}", response_model=ResourceResponse)
async def get_resource(
    resource_id: int,
    db: Session = Depend(get_db)
):
    """Get resource details."""
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    
    return resource


@router.get("/{resource_id}/content", response_model=ResourceContentResponse)
async def get_resource_content(
    resource_id: int,
    db: Session = Depend(get_db)
):
    """Get resource content preview."""
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    
    content = resource.extracted_content or ""
    preview = content[:500] if len(content) > 500 else content
    
    return ResourceContentResponse(
        id=resource.id,
        resource_type=resource.resource_type.value,
        file_name=resource.file_name,
        source_url=resource.source_url,
        content_preview=preview,
        total_length=len(content),
        status=resource.status.value
    )


@router.put("/{resource_id}", response_model=ResourceResponse)
async def update_resource(
    resource_id: int,
    resource_data: ResourceUpdate,
    db: Session = Depend(get_db)
):
    """Update resource (e.g., activate/deactivate)."""
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    
    if resource_data.is_active is not None:
        resource.is_active = 1 if resource_data.is_active else 0
        resource.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(resource)
    
    return resource


@router.post("/{resource_id}/reprocess", response_model=ResourceResponse)
async def reprocess_resource(
    resource_id: int,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depend(get_db)
):
    """Reprocess a failed or completed resource."""
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    
    # Reset to pending
    resource.status = ResourceStatus.PENDING
    resource.error_message = None
    db.commit()
    db.refresh(resource)
    
    # Process based on type
    if resource.resource_type == ResourceType.PDF:
        background_tasks.add_task(process_resource_task, resource.id, "PDF", resource.file_path)
    elif resource.resource_type == ResourceType.WEBSITE:
        background_tasks.add_task(process_resource_task, resource.id, "WEBSITE")
    elif resource.resource_type == ResourceType.FACEBOOK:
        background_tasks.add_task(process_resource_task, resource.id, "FACEBOOK")
    
    return resource


@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resource(
    resource_id: int,
    db: Session = Depend(get_db)
):
    """Delete a resource and its associated file."""
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    
    # Delete file if it exists
    if resource.file_path and os.path.exists(resource.file_path):
        try:
            os.remove(resource.file_path)
        except Exception as e:
            # Log but don't fail the deletion
            print(f"Failed to delete file: {str(e)}")
    
    # Delete database entry
    db.delete(resource)
    db.commit()
    
    return None
