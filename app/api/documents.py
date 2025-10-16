"""
Document API endpoints.
"""
import shutil
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Query
from sqlalchemy.orm import Session
import logging

from app.db.database import get_db
from app.models.document import Document, CapitalCallDetail, DistributionDetail, ProcessingLog
from app.schemas.schemas import (
    DocumentResponse, DocumentDetailResponse, DocumentSearchRequest, DocumentSearchResponse,
    CapitalCallDetailResponse, DistributionDetailResponse, UploadResponse
)
from app.core.security import get_current_active_user
from app.models.user import User
from app.services.document_processor import DocumentProcessor
from app.services.lp_extractor import LPDocumentExtractor
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])

# Initialize services
document_processor = DocumentProcessor()
lp_extractor = LPDocumentExtractor()

# Ensure upload directory exists
upload_dir = Path(settings.upload_dir)
upload_dir.mkdir(exist_ok=True)


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upload a document for processing.
    """
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        file_extension = Path(file.filename).suffix.lower().lstrip('.')
        if file_extension not in settings.allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(settings.allowed_extensions)}"
            )
        
        # Validate file size
        file_content = await file.read()
        if len(file_content) > settings.max_file_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {settings.max_file_size} bytes"
            )
        
        # Reset file pointer
        await file.seek(0)
        
        # Save file
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = upload_dir / safe_filename
        
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Create database record
        db_document = Document(
            filename=safe_filename,
            original_filename=file.filename,
            file_path=str(file_path),
            file_size=len(file_content),
            mime_type=file.content_type or "application/octet-stream",
            processing_status="pending",
            uploaded_by_id=current_user.id
        )
        
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        
        logger.info(f"Document uploaded successfully: {db_document.id}")
        
        return UploadResponse(
            document_id=db_document.id,
            message="Document uploaded successfully",
            processing_status="pending"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail="Upload failed")


@router.post("/{document_id}/process")
async def process_document(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Process a document to extract structured data.
    """
    try:
        # Get document from database
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        if document.processing_status == "processing":
            raise HTTPException(status_code=409, detail="Document is already being processed")
        
        if document.processing_status == "completed":
            raise HTTPException(status_code=409, detail="Document already processed")
        
        # Update status to processing
        document.processing_status = "processing"
        db.commit()
        
        try:
            # Process document
            file_path = Path(document.file_path)
            if not file_path.exists():
                raise HTTPException(status_code=404, detail="Document file not found")
            
            # Process with document processor
            processing_result = await document_processor.process_document(file_path)
            
            # Update document with processing results
            document.ocr_text = processing_result.get("ocr_text", "")
            document.structured_data = processing_result.get("docling_result", {})
            document.processing_status = "completed"
            document.processed_at = datetime.utcnow()
            
            # Classify document type
            docling_result = processing_result.get("docling_result", {})
            text_content = docling_result.get("text_content", "")
            structured_data = docling_result.get("structured_data", {})
            
            document.document_type = document_processor.classify_document_type(text_content, structured_data)
            
            # Extract fund information
            fund_info = document_processor.extract_fund_information(text_content)
            document.fund_name = fund_info.get("fund_name")
            document.fund_id = fund_info.get("fund_id")
            
            # Extract specialized data based on document type
            if document.document_type == "capital_call":
                capital_call_data = lp_extractor.extract_capital_call_data(text_content)
                if capital_call_data:
                    # Create or update capital call details
                    capital_call_detail = db.query(CapitalCallDetail).filter(
                        CapitalCallDetail.document_id == document_id
                    ).first()
                    
                    if not capital_call_detail:
                        capital_call_detail = CapitalCallDetail(document_id=document_id)
                        db.add(capital_call_detail)
                    
                    # Update fields
                    for key, value in capital_call_data.items():
                        if hasattr(capital_call_detail, key) and value is not None:
                            setattr(capital_call_detail, key, value)
            
            elif document.document_type == "distribution":
                distribution_data = lp_extractor.extract_distribution_data(text_content)
                if distribution_data:
                    # Create or update distribution details
                    distribution_detail = db.query(DistributionDetail).filter(
                        DistributionDetail.document_id == document_id
                    ).first()
                    
                    if not distribution_detail:
                        distribution_detail = DistributionDetail(document_id=document_id)
                        db.add(distribution_detail)
                    
                    # Update fields
                    for key, value in distribution_data.items():
                        if hasattr(distribution_detail, key) and value is not None:
                            setattr(distribution_detail, key, value)
            
            db.commit()
            
            logger.info(f"Document processed successfully: {document_id}")
            
            return {
                "message": "Document processed successfully",
                "document_type": document.document_type,
                "extraction_confidence": document.extraction_confidence
            }
            
        except Exception as e:
            # Update status to failed
            document.processing_status = "failed"
            db.commit()
            
            # Log error
            error_log = ProcessingLog(
                document_id=document_id,
                log_level="ERROR",
                message=f"Processing failed: {str(e)}",
                step="processing"
            )
            db.add(error_log)
            db.commit()
            
            logger.error(f"Document processing failed: {document_id} - {str(e)}")
            raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Processing error: {str(e)}")
        raise HTTPException(status_code=500, detail="Processing failed")


@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    document_type: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List documents with optional filtering.
    """
    try:
        query = db.query(Document)
        
        if document_type:
            query = query.filter(Document.document_type == document_type)
        
        documents = query.offset(skip).limit(limit).all()
        
        return documents
        
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list documents")


@router.get("/{document_id}", response_model=DocumentDetailResponse)
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific document.
    """
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return document
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get document")


@router.get("/{document_id}/capital-call", response_model=CapitalCallDetailResponse)
async def get_capital_call_details(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get capital call details for a document.
    """
    try:
        capital_call = db.query(CapitalCallDetail).filter(
            CapitalCallDetail.document_id == document_id
        ).first()
        
        if not capital_call:
            raise HTTPException(status_code=404, detail="Capital call details not found")
        
        return capital_call
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting capital call details: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get capital call details")


@router.get("/{document_id}/distribution", response_model=DistributionDetailResponse)
async def get_distribution_details(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get distribution details for a document.
    """
    try:
        distribution = db.query(DistributionDetail).filter(
            DistributionDetail.document_id == document_id
        ).first()
        
        if not distribution:
            raise HTTPException(status_code=404, detail="Distribution details not found")
        
        return distribution
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting distribution details: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get distribution details")


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a document and its associated files.
    """
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete file from filesystem
        file_path = Path(document.file_path)
        if file_path.exists():
            file_path.unlink()
        
        # Delete from database
        db.delete(document)
        db.commit()
        
        logger.info(f"Document deleted: {document_id}")
        
        return {"message": "Document deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete document")
