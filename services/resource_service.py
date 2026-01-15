"""
Resource Management Service
Handles resource processing and knowledge base management.
"""

import os
import json
import logging
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session

from models import Resource, ResourceType, ResourceStatus
from services.pdf_processor import PDFProcessor
from services.web_scraper import WebScraper

logger = logging.getLogger(__name__)


class ResourceService:
    """Service for managing company resources and knowledge base."""
    
    @staticmethod
    async def process_pdf_resource(resource: Resource, file_path: str, db: Session) -> bool:
        """
        Process a PDF resource and extract content.
        
        Args:
            resource: Resource database object
            file_path: Path to the PDF file
            db: Database session
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Processing PDF resource ID {resource.id}")
            
            # Update status to processing
            resource.status = ResourceStatus.PROCESSING
            db.commit()
            
            # Extract text
            text, error = await PDFProcessor.extract_text(file_path)
            
            if text:
                # Get metadata
                metadata = PDFProcessor.get_pdf_metadata(file_path)
                
                # Update resource
                resource.extracted_content = text
                resource.resource_metadata = json.dumps(metadata)
                resource.status = ResourceStatus.COMPLETED
                resource.processed_at = datetime.utcnow()
                resource.error_message = None
                
                db.commit()
                logger.info(f"Successfully processed PDF resource ID {resource.id}")
                return True
            else:
                # Update with error
                resource.status = ResourceStatus.FAILED
                resource.error_message = error or "Failed to extract content"
                db.commit()
                logger.error(f"Failed to process PDF resource ID {resource.id}: {error}")
                return False
                
        except Exception as e:
            error_msg = f"Error processing PDF resource: {str(e)}"
            logger.error(error_msg)
            resource.status = ResourceStatus.FAILED
            resource.error_message = error_msg
            db.commit()
            return False
    
    @staticmethod
    async def process_website_resource(resource: Resource, db: Session) -> bool:
        """
        Process a website resource and extract content.
        
        Args:
            resource: Resource database object
            db: Database session
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Processing website resource ID {resource.id}")
            
            # Update status to processing
            resource.status = ResourceStatus.PROCESSING
            db.commit()
            
            # Scrape website
            text, error, metadata = await WebScraper.scrape_website(resource.source_url)
            
            if text:
                # Update resource
                resource.extracted_content = text
                resource.resource_metadata = json.dumps(metadata) if metadata else None
                resource.status = ResourceStatus.COMPLETED
                resource.processed_at = datetime.utcnow()
                resource.error_message = None
                
                db.commit()
                logger.info(f"Successfully processed website resource ID {resource.id}")
                return True
            else:
                # Update with error
                resource.status = ResourceStatus.FAILED
                resource.error_message = error or "Failed to extract content"
                db.commit()
                logger.error(f"Failed to process website resource ID {resource.id}: {error}")
                return False
                
        except Exception as e:
            error_msg = f"Error processing website resource: {str(e)}"
            logger.error(error_msg)
            resource.status = ResourceStatus.FAILED
            resource.error_message = error_msg
            db.commit()
            return False
    
    @staticmethod
    async def process_facebook_resource(resource: Resource, db: Session) -> bool:
        """
        Process a Facebook page resource and extract content.
        
        Args:
            resource: Resource database object
            db: Database session
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Processing Facebook resource ID {resource.id}")
            
            # Update status to processing
            resource.status = ResourceStatus.PROCESSING
            db.commit()
            
            # Scrape Facebook page
            text, error, metadata = await WebScraper.scrape_facebook_page(resource.source_url)
            
            if text:
                # Update resource
                resource.extracted_content = text
                resource.resource_metadata = json.dumps(metadata) if metadata else None
                resource.status = ResourceStatus.COMPLETED
                resource.processed_at = datetime.utcnow()
                resource.error_message = None
                
                db.commit()
                logger.info(f"Successfully processed Facebook resource ID {resource.id}")
                return True
            else:
                # Update with error
                resource.status = ResourceStatus.FAILED
                resource.error_message = error or "Failed to extract content"
                db.commit()
                logger.error(f"Failed to process Facebook resource ID {resource.id}: {error}")
                return False
                
        except Exception as e:
            error_msg = f"Error processing Facebook resource: {str(e)}"
            logger.error(error_msg)
            resource.status = ResourceStatus.FAILED
            resource.error_message = error_msg
            db.commit()
            return False
    
    @staticmethod
    async def process_text_resource(resource: Resource, text_content: str, db: Session) -> bool:
        """
        Process a text resource.
        
        Args:
            resource: Resource database object
            text_content: The text content to store
            db: Database session
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Processing text resource ID {resource.id}")
            
            # Update resource
            resource.extracted_content = text_content
            resource.status = ResourceStatus.COMPLETED
            resource.processed_at = datetime.utcnow()
            resource.error_message = None
            
            db.commit()
            logger.info(f"Successfully processed text resource ID {resource.id}")
            return True
                
        except Exception as e:
            error_msg = f"Error processing text resource: {str(e)}"
            logger.error(error_msg)
            resource.status = ResourceStatus.FAILED
            resource.error_message = error_msg
            db.commit()
            return False
    
    @staticmethod
    def get_company_knowledge_base(company_id: int, db: Session, max_length: int = 15000) -> str:
        """
        Get combined knowledge base for a company to use in AI prompts.
        
        Args:
            company_id: Company ID
            db: Database session
            max_length: Maximum character length to return
            
        Returns:
            Combined knowledge base text
        """
        try:
            # Get all active, completed resources for the company
            resources = db.query(Resource).filter(
                Resource.company_id == company_id,
                Resource.status == ResourceStatus.COMPLETED,
                Resource.is_active == 1
            ).all()
            
            if not resources:
                return ""
            
            knowledge_parts = []
            current_length = 0
            
            for resource in resources:
                if not resource.extracted_content:
                    continue
                
                # Add resource header
                header = f"\n\n--- {resource.resource_type} Resource"
                if resource.file_name:
                    header += f": {resource.file_name}"
                elif resource.source_url:
                    header += f": {resource.source_url}"
                header += " ---\n\n"
                
                content = header + resource.extracted_content
                
                # Check if adding this would exceed max length
                if current_length + len(content) > max_length:
                    # Add truncated version
                    remaining = max_length - current_length
                    if remaining > 200:  # Only add if there's meaningful space left
                        knowledge_parts.append(content[:remaining] + "\n\n[Content truncated...]")
                    break
                
                knowledge_parts.append(content)
                current_length += len(content)
            
            knowledge_base = "\n".join(knowledge_parts)
            logger.info(f"Retrieved knowledge base for company {company_id}: {len(knowledge_base)} characters from {len(resources)} resources")
            
            return knowledge_base
            
        except Exception as e:
            logger.error(f"Error getting knowledge base for company {company_id}: {str(e)}")
            return ""
    
    @staticmethod
    def get_resource_stats(company_id: int, db: Session) -> dict:
        """
        Get statistics about company resources.
        
        Args:
            company_id: Company ID
            db: Database session
            
        Returns:
            Dictionary with statistics
        """
        try:
            total = db.query(Resource).filter(
                Resource.company_id == company_id
            ).count()
            
            completed = db.query(Resource).filter(
                Resource.company_id == company_id,
                Resource.status == ResourceStatus.COMPLETED
            ).count()
            
            processing = db.query(Resource).filter(
                Resource.company_id == company_id,
                Resource.status == ResourceStatus.PROCESSING
            ).count()
            
            failed = db.query(Resource).filter(
                Resource.company_id == company_id,
                Resource.status == ResourceStatus.FAILED
            ).count()
            
            return {
                "total": total,
                "completed": completed,
                "processing": processing,
                "failed": failed,
                "pending": total - completed - processing - failed
            }
            
        except Exception as e:
            logger.error(f"Error getting resource stats: {str(e)}")
            return {
                "total": 0,
                "completed": 0,
                "processing": 0,
                "failed": 0,
                "pending": 0
            }
