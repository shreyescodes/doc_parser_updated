"""
Document processing service using Docling and OCR.
"""
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

try:
    from docling.document_converter import DocumentConverter
    from docling.datamodel.base_models import ConversionResult
    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

try:
    import pdf2image
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False
from app.core.config import settings

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Main document processing service."""
    
    def __init__(self):
        if DOCLING_AVAILABLE:
            self.converter = DocumentConverter()
        else:
            self.converter = None
        self.tesseract_config = f'--tessdata-dir /usr/share/tesseract-ocr/4.00/tessdata'
    
    async def process_document(self, file_path: Path) -> Dict[str, Any]:
        """
        Process a document using Docling and OCR.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Dictionary containing processed document data
        """
        try:
            logger.info(f"Starting document processing for: {file_path}")
            
            # Extract text using Docling
            docling_result = await self._process_with_docling(file_path)
            
            # Extract text using OCR as fallback/verification
            ocr_text = await self._extract_text_with_ocr(file_path)
            
            # Combine results
            result = {
                "docling_result": docling_result,
                "ocr_text": ocr_text,
                "processed_at": datetime.utcnow().isoformat(),
                "file_path": str(file_path),
                "file_size": file_path.stat().st_size
            }
            
            logger.info(f"Document processing completed for: {file_path}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {str(e)}")
            raise
    
    async def _process_with_docling(self, file_path: Path) -> Dict[str, Any]:
        """
        Process document using Docling for structured extraction.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Dictionary containing Docling processing results
        """
        if not DOCLING_AVAILABLE or not self.converter:
            logger.warning("Docling not available, skipping Docling processing")
            return {
                "structured_data": None,
                "text_content": None,
                "success": False,
                "error": "Docling not installed",
                "processing_method": "docling"
            }
        
        try:
            logger.info(f"Processing with Docling: {file_path}")
            
            # Convert the document
            conv_result: ConversionResult = self.converter.convert(file_path)
            
            # Export to structured format
            structured_data = conv_result.document.export_to_dict(with_images=False)
            
            # Extract text content
            text_content = conv_result.document.export_to_markdown()
            
            return {
                "structured_data": structured_data,
                "text_content": text_content,
                "success": True,
                "processing_method": "docling"
            }
            
        except Exception as e:
            logger.error(f"Docling processing failed for {file_path}: {str(e)}")
            return {
                "structured_data": None,
                "text_content": None,
                "success": False,
                "error": str(e),
                "processing_method": "docling"
            }
    
    async def _extract_text_with_ocr(self, file_path: Path) -> str:
        """
        Extract text using OCR as fallback method.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Extracted text string
        """
        if not TESSERACT_AVAILABLE or not PILLOW_AVAILABLE:
            logger.warning("OCR dependencies not available, skipping OCR processing")
            return ""
        
        try:
            logger.info(f"Extracting text with OCR: {file_path}")
            
            # Convert PDF to images if needed
            if file_path.suffix.lower() == '.pdf':
                if not PDF2IMAGE_AVAILABLE:
                    logger.warning("pdf2image not available, cannot process PDF")
                    return ""
                
                images = pdf2image.convert_from_path(file_path)
                text_parts = []
                
                for i, image in enumerate(images):
                    # Convert PIL image to RGB if needed
                    if image.mode != 'RGB':
                        image = image.convert('RGB')
                    
                    # Extract text from image
                    page_text = pytesseract.image_to_string(
                        image, 
                        lang=settings.tesseract_lang,
                        config=self.tesseract_config
                    )
                    text_parts.append(f"--- Page {i+1} ---\n{page_text}")
                
                return "\n\n".join(text_parts)
            
            else:
                # Process as image
                image = Image.open(file_path)
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                text = pytesseract.image_to_string(
                    image,
                    lang=settings.tesseract_lang,
                    config=self.tesseract_config
                )
                
                return text
                
        except Exception as e:
            logger.error(f"OCR processing failed for {file_path}: {str(e)}")
            return ""
    
    def classify_document_type(self, text_content: str, structured_data: Dict[str, Any]) -> str:
        """
        Classify document type based on content analysis.
        
        Args:
            text_content: Extracted text content
            structured_data: Structured data from Docling
            
        Returns:
            Document type classification
        """
        try:
            text_lower = text_content.lower()
            
            # Capital call indicators
            capital_call_keywords = [
                'capital call', 'call notice', 'capital contribution',
                'commitment', 'drawdown', 'capital request',
                'contribution request', 'funding request'
            ]
            
            # Distribution indicators
            distribution_keywords = [
                'distribution', 'dividend', 'return of capital',
                'proceeds', 'distribution notice', 'cash distribution',
                'return to limited partners'
            ]
            
            # Check for capital call
            capital_call_score = sum(1 for keyword in capital_call_keywords if keyword in text_lower)
            
            # Check for distribution
            distribution_score = sum(1 for keyword in distribution_keywords if keyword in text_lower)
            
            # Classify based on scores
            if capital_call_score > distribution_score and capital_call_score > 0:
                return "capital_call"
            elif distribution_score > capital_call_score and distribution_score > 0:
                return "distribution"
            else:
                return "other"
                
        except Exception as e:
            logger.error(f"Document classification failed: {str(e)}")
            return "other"
    
    def extract_fund_information(self, text_content: str) -> Dict[str, str]:
        """
        Extract fund information from document text.
        
        Args:
            text_content: Extracted text content
            
        Returns:
            Dictionary containing fund information
        """
        try:
            fund_info = {}
            text_lower = text_content.lower()
            
            # Common patterns for fund information
            patterns = {
                'fund_name': ['fund name', 'fund:', 'investment fund'],
                'fund_id': ['fund id', 'fund identifier', 'fund number'],
                'fund_size': ['fund size', 'total commitments', 'fund commitments']
            }
            
            # Simple extraction logic - can be enhanced with regex
            lines = text_content.split('\n')
            for line in lines:
                line_lower = line.lower()
                for key, keywords in patterns.items():
                    for keyword in keywords:
                        if keyword in line_lower:
                            # Extract value after colon or keyword
                            if ':' in line:
                                value = line.split(':', 1)[1].strip()
                                if value:
                                    fund_info[key] = value
                            break
            
            return fund_info
            
        except Exception as e:
            logger.error(f"Fund information extraction failed: {str(e)}")
            return {}
