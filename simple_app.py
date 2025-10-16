"""
Simple document parser application for testing.
This version works with minimal dependencies and extracts real content.
"""
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import json
import os
from datetime import datetime
from pathlib import Path
import shutil
import PyPDF2
import re

app = FastAPI(
    title="Simple Document Parser",
    description="Simple document parsing API for testing",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Simple response models
class DocumentResponse(BaseModel):
    document_id: str
    filename: str
    file_size: int
    extracted_data: Dict[str, Any]
    processing_status: str
    message: str

class SimpleUploadResponse(BaseModel):
    document_id: str
    filename: str
    message: str

# Enhanced document processor with real content extraction
class SimpleDocumentProcessor:
    def __init__(self):
        self.supported_formats = ['.pdf', '.txt']
    
    def extract_text_from_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file."""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            return f"Error extracting PDF text: {str(e)}"
    
    def extract_text_from_txt(self, file_path: Path) -> str:
        """Extract text from TXT file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            return f"Error extracting text: {str(e)}"
    
    def extract_structured_data(self, text: str) -> Dict[str, Any]:
        """Extract structured data from text content."""
        try:
            structured_data = {
                "contact_info": self.extract_contact_info(text),
                "dates": self.extract_dates(text),
                "numbers": self.extract_numbers(text),
                "emails": self.extract_emails(text),
                "phones": self.extract_phones(text),
                "addresses": self.extract_addresses(text),
                "skills": self.extract_skills(text),
                "education": self.extract_education(text),
                "experience": self.extract_experience(text)
            }
            return structured_data
        except Exception as e:
            return {"error": f"Structured extraction failed: {str(e)}"}
    
    def extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract contact information."""
        contact_info = {}
        
        # Extract name (usually at the beginning)
        lines = text.split('\n')[:5]  # Check first 5 lines
        for line in lines:
            line = line.strip()
            if len(line) > 3 and len(line.split()) <= 3:  # Likely a name
                contact_info["name"] = line
                break
        
        return contact_info
    
    def extract_emails(self, text: str) -> list:
        """Extract email addresses."""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(email_pattern, text)
    
    def extract_phones(self, text: str) -> list:
        """Extract phone numbers."""
        phone_pattern = r'(\+?1[-.\s]?)?(\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4})'
        return re.findall(phone_pattern, text)
    
    def extract_dates(self, text: str) -> list:
        """Extract dates."""
        date_patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # MM/DD/YYYY or DD/MM/YYYY
            r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',    # YYYY/MM/DD
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b'  # Month DD, YYYY
        ]
        dates = []
        for pattern in date_patterns:
            dates.extend(re.findall(pattern, text))
        return dates
    
    def extract_numbers(self, text: str) -> Dict[str, list]:
        """Extract various types of numbers."""
        return {
            "years": re.findall(r'\b(19|20)\d{2}\b', text),
            "percentages": re.findall(r'\b\d+\.?\d*\s*%\b', text),
            "amounts": re.findall(r'\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?', text)
        }
    
    def extract_addresses(self, text: str) -> list:
        """Extract potential addresses."""
        address_pattern = r'\d+\s+[A-Za-z0-9\s,.-]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd|Way|Place|Pl)'
        return re.findall(address_pattern, text, re.IGNORECASE)
    
    def extract_skills(self, text: str) -> list:
        """Extract skills/keywords."""
        common_skills = [
            'Python', 'JavaScript', 'Java', 'C++', 'C#', 'React', 'Angular', 'Vue',
            'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'AWS', 'Azure', 'Docker',
            'Git', 'Linux', 'Windows', 'Machine Learning', 'AI', 'Data Science',
            'Web Development', 'Mobile Development', 'UI/UX', 'Agile', 'Scrum'
        ]
        
        found_skills = []
        text_lower = text.lower()
        for skill in common_skills:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        return found_skills
    
    def extract_education(self, text: str) -> list:
        """Extract education information."""
        education_keywords = ['university', 'college', 'degree', 'bachelor', 'master', 'phd', 'diploma']
        lines = text.split('\n')
        education_lines = []
        
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in education_keywords):
                education_lines.append(line.strip())
        
        return education_lines
    
    def extract_experience(self, text: str) -> list:
        """Extract work experience information."""
        experience_keywords = ['experience', 'work', 'job', 'position', 'role', 'employed']
        lines = text.split('\n')
        experience_lines = []
        
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in experience_keywords):
                experience_lines.append(line.strip())
        
        return experience_lines
    
    def process_document(self, file_path: Path, filename: str) -> Dict[str, Any]:
        """Process document and extract real content."""
        try:
            file_size = file_path.stat().st_size
            file_extension = file_path.suffix.lower()
            
            # Extract text based on file type
            if file_extension == '.pdf':
                extracted_text = self.extract_text_from_pdf(file_path)
            elif file_extension == '.txt':
                extracted_text = self.extract_text_from_txt(file_path)
            else:
                extracted_text = "Unsupported file type"
            
            # Extract structured data
            structured_data = self.extract_structured_data(extracted_text)
            
            # Determine document type based on content
            document_type = self.classify_document(extracted_text)
            
            result = {
                "file_info": {
                    "filename": filename,
                    "file_size": file_size,
                    "file_type": file_extension,
                    "processed_at": datetime.utcnow().isoformat()
                },
                "extracted_text": extracted_text,
                "document_type": document_type,
                "confidence": 0.9 if extracted_text and not extracted_text.startswith("Error") else 0.3,
                "structured_data": structured_data,
                "metadata": {
                    "text_length": len(extracted_text),
                    "word_count": len(extracted_text.split()) if extracted_text else 0,
                    "processing_method": "enhanced_extractor"
                }
            }
            
            return result
            
        except Exception as e:
            return {
                "error": f"Processing failed: {str(e)}",
                "file_info": {
                    "filename": filename,
                    "file_size": file_path.stat().st_size if file_path.exists() else 0,
                    "file_type": file_path.suffix.lower(),
                    "processed_at": datetime.utcnow().isoformat()
                }
            }
    
    def classify_document(self, text: str) -> str:
        """Classify document type based on content."""
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in ['resume', 'cv', 'curriculum vitae', 'experience', 'education']):
            return "resume"
        elif any(keyword in text_lower for keyword in ['invoice', 'bill', 'payment', 'amount due']):
            return "invoice"
        elif any(keyword in text_lower for keyword in ['contract', 'agreement', 'terms', 'conditions']):
            return "contract"
        elif any(keyword in text_lower for keyword in ['report', 'analysis', 'summary', 'findings']):
            return "report"
        else:
            return "document"

# Initialize processor
processor = SimpleDocumentProcessor()

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Simple Document Parser API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "POST /upload",
            "health": "GET /health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.post("/upload", response_model=SimpleUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document for processing.
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in processor.supported_formats:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Supported: {', '.join(processor.supported_formats)}"
            )
        
        # Save file
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = UPLOAD_DIR / safe_filename
        
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Generate document ID
        document_id = f"doc_{timestamp}"
        
        return SimpleUploadResponse(
            document_id=document_id,
            filename=safe_filename,
            message="Document uploaded successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/process/{document_id}", response_model=DocumentResponse)
async def process_document(document_id: str, filename: str = Query(...)):
    """
    Process a document to extract structured data.
    """
    try:
        # Find the file
        file_path = None
        for file in UPLOAD_DIR.iterdir():
            if file.is_file() and document_id in file.name:
                file_path = file
                break
        
        if not file_path or not file_path.exists():
            raise HTTPException(status_code=404, detail="Document file not found")
        
        # Process document
        extracted_data = processor.process_document(file_path, filename)
        
        return DocumentResponse(
            document_id=document_id,
            filename=filename,
            file_size=file_path.stat().st_size,
            extracted_data=extracted_data,
            processing_status="completed",
            message="Document processed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.post("/process-file", response_model=DocumentResponse)
async def process_uploaded_file(file: UploadFile = File(...)):
    """
    Upload and process a document in one step.
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in processor.supported_formats:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Supported: {', '.join(processor.supported_formats)}"
            )
        
        # Save file temporarily
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = UPLOAD_DIR / safe_filename
        
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process document immediately
        document_id = f"doc_{timestamp}"
        extracted_data = processor.process_document(file_path, file.filename)
        
        return DocumentResponse(
            document_id=document_id,
            filename=file.filename,
            file_size=file_path.stat().st_size,
            extracted_data=extracted_data,
            processing_status="completed",
            message="Document uploaded and processed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.get("/documents", response_model=list)
async def list_documents():
    """
    List all uploaded documents.
    """
    try:
        documents = []
        for file in UPLOAD_DIR.iterdir():
            if file.is_file():
                documents.append({
                    "filename": file.name,
                    "file_size": file.stat().st_size,
                    "created_at": datetime.fromtimestamp(file.stat().st_ctime).isoformat(),
                    "file_type": file.suffix.lower()
                })
        
        return documents
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")

@app.get("/documents/{document_id}")
async def get_document(document_id: str):
    """
    Get document details and extracted data.
    """
    try:
        # Find the file
        file_path = None
        for file in UPLOAD_DIR.iterdir():
            if file.is_file() and document_id in file.name:
                file_path = file
                break
        
        if not file_path or not file_path.exists():
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Process document if not already processed
        extracted_data = processor.process_document(file_path, file_path.name)
        
        return {
            "document_id": document_id,
            "filename": file_path.name,
            "file_size": file_path.stat().st_size,
            "extracted_data": extracted_data,
            "processing_status": "completed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get document: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("simple_app:app", host="0.0.0.0", port=8000, reload=True)
