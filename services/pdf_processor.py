"""
PDF Content Extraction Service
Extracts text content from PDF files.
"""

import PyPDF2
import pdfplumber
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Service for processing PDF files and extracting content."""
    
    @staticmethod
    async def extract_text_pypdf2(file_path: str) -> Optional[str]:
        """
        Extract text from PDF using PyPDF2.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text content or None if failed
        """
        try:
            text_content = []
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                logger.info(f"Extracting text from {total_pages} pages using PyPDF2")
                
                for page_num in range(total_pages):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
                
                return "\n\n".join(text_content)
                
        except Exception as e:
            logger.error(f"PyPDF2 extraction failed: {str(e)}")
            return None
    
    @staticmethod
    async def extract_text_pdfplumber(file_path: str) -> Optional[str]:
        """
        Extract text from PDF using pdfplumber (more accurate for tables).
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text content or None if failed
        """
        try:
            text_content = []
            
            with pdfplumber.open(file_path) as pdf:
                total_pages = len(pdf.pages)
                logger.info(f"Extracting text from {total_pages} pages using pdfplumber")
                
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
                    
                    # Also extract tables
                    tables = page.extract_tables()
                    for table in tables:
                        # Convert table to text representation
                        table_text = "\n".join(["\t".join([str(cell) if cell else "" for cell in row]) for row in table])
                        if table_text:
                            text_content.append(f"\n[TABLE]\n{table_text}\n[/TABLE]\n")
                
                return "\n\n".join(text_content)
                
        except Exception as e:
            logger.error(f"pdfplumber extraction failed: {str(e)}")
            return None
    
    @staticmethod
    async def extract_text(file_path: str) -> tuple[Optional[str], Optional[str]]:
        """
        Extract text from PDF using both methods and return the best result.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Tuple of (extracted_text, error_message)
        """
        try:
            # Try pdfplumber first (better for complex layouts)
            logger.info(f"Starting PDF extraction for: {file_path}")
            text = await PDFProcessor.extract_text_pdfplumber(file_path)
            
            # If pdfplumber fails or returns empty, try PyPDF2
            if not text or len(text.strip()) < 100:
                logger.info("pdfplumber extraction insufficient, trying PyPDF2")
                text = await PDFProcessor.extract_text_pypdf2(file_path)
            
            if text and len(text.strip()) > 0:
                logger.info(f"Successfully extracted {len(text)} characters")
                return text, None
            else:
                error_msg = "No text content could be extracted from PDF"
                logger.error(error_msg)
                return None, error_msg
                
        except Exception as e:
            error_msg = f"PDF processing error: {str(e)}"
            logger.error(error_msg)
            return None, error_msg
    
    @staticmethod
    def get_pdf_metadata(file_path: str) -> dict:
        """
        Get metadata from PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary containing metadata
        """
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                metadata = pdf_reader.metadata
                
                return {
                    "pages": len(pdf_reader.pages),
                    "title": metadata.get("/Title", ""),
                    "author": metadata.get("/Author", ""),
                    "subject": metadata.get("/Subject", ""),
                    "creator": metadata.get("/Creator", ""),
                    "producer": metadata.get("/Producer", ""),
                }
        except Exception as e:
            logger.error(f"Failed to get PDF metadata: {str(e)}")
            return {}
