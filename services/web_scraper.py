"""
Web Content Extraction Service
Scrapes and extracts text content from websites and Facebook pages.
"""

import requests
from bs4 import BeautifulSoup
import logging
from typing import Optional, Dict
from urllib.parse import urljoin, urlparse
import re

logger = logging.getLogger(__name__)


class WebScraper:
    """Service for scraping web content."""
    
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Validate URL format."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    @staticmethod
    async def scrape_website(url: str) -> tuple[Optional[str], Optional[str], Optional[Dict]]:
        """
        Scrape content from a website.
        
        Args:
            url: Website URL to scrape
            
        Returns:
            Tuple of (extracted_text, error_message, metadata)
        """
        try:
            if not WebScraper.is_valid_url(url):
                return None, "Invalid URL format", None
            
            logger.info(f"Scraping website: {url}")
            
            headers = {
                'User-Agent': WebScraper.USER_AGENT,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Get page title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else ""
            
            # Get meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc.get('content', '').strip() if meta_desc else ""
            
            # Extract main content
            # Try to find main content area
            main_content = (
                soup.find('main') or 
                soup.find('article') or 
                soup.find('div', class_=re.compile(r'content|main|article', re.I)) or
                soup.find('body')
            )
            
            # Get text
            if main_content:
                text = main_content.get_text(separator='\n', strip=True)
            else:
                text = soup.get_text(separator='\n', strip=True)
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Create metadata
            metadata = {
                "url": url,
                "title": title_text,
                "description": description,
                "content_length": len(text),
            }
            
            # Get all links
            links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                absolute_url = urljoin(url, href)
                if absolute_url.startswith('http'):
                    links.append(absolute_url)
            
            metadata["links_found"] = len(links)
            
            if text and len(text.strip()) > 100:
                logger.info(f"Successfully scraped {len(text)} characters from {url}")
                
                # Add title and description to the beginning
                full_content = f"# {title_text}\n\n{description}\n\n{text}"
                
                return full_content, None, metadata
            else:
                error_msg = "No substantial content could be extracted from the website"
                logger.error(error_msg)
                return None, error_msg, metadata
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to fetch website: {str(e)}"
            logger.error(error_msg)
            return None, error_msg, None
        except Exception as e:
            error_msg = f"Website scraping error: {str(e)}"
            logger.error(error_msg)
            return None, error_msg, None
    
    @staticmethod
    async def scrape_facebook_page(url: str) -> tuple[Optional[str], Optional[str], Optional[Dict]]:
        """
        Scrape content from a Facebook page.
        Note: This is a basic implementation. Facebook heavily restricts scraping.
        For production, consider using the official Facebook Graph API.
        
        Args:
            url: Facebook page URL
            
        Returns:
            Tuple of (extracted_text, error_message, metadata)
        """
        try:
            if not WebScraper.is_valid_url(url):
                return None, "Invalid URL format", None
            
            if 'facebook.com' not in url.lower():
                return None, "URL is not a Facebook page", None
            
            logger.info(f"Scraping Facebook page: {url}")
            
            headers = {
                'User-Agent': WebScraper.USER_AGENT,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Try to extract page title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else ""
            
            # Try to extract meta description
            meta_desc = soup.find('meta', attrs={'property': 'og:description'})
            description = meta_desc.get('content', '').strip() if meta_desc else ""
            
            # Extract any visible text (Facebook's content is usually JS-rendered, so this is limited)
            text = soup.get_text(separator='\n', strip=True)
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            text = '\n'.join(line for line in lines if line)
            
            metadata = {
                "url": url,
                "title": title_text,
                "description": description,
                "note": "Limited content extraction - Facebook requires API access for full content"
            }
            
            if description or (text and len(text) > 50):
                content = f"# {title_text}\n\n{description}\n\nNote: This is limited public information from the Facebook page. For comprehensive access, please use Facebook Graph API.\n\n{text[:1000]}"
                logger.warning("Facebook page scraped with limited content")
                return content, None, metadata
            else:
                error_msg = "Unable to extract content from Facebook page. Consider using Facebook Graph API for better results."
                logger.error(error_msg)
                return None, error_msg, metadata
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to fetch Facebook page: {str(e)}"
            logger.error(error_msg)
            return None, error_msg, None
        except Exception as e:
            error_msg = f"Facebook scraping error: {str(e)}"
            logger.error(error_msg)
            return None, error_msg, None
