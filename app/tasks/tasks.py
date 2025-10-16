"""
Celery tasks for background processing.
"""
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import List

from celery import current_task
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from app.core.config import settings
from app.models.document import Document, ProcessingLog, CapitalCallDetail, DistributionDetail
from app.services.document_processor import DocumentProcessor
from app.services.lp_extractor import LPDocumentExtractor
from app.tasks.celery_app import celery_app

# Database setup for Celery tasks
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialize services
document_processor = DocumentProcessor()
lp_extractor = LPDocumentExtractor()


@celery_app.task(bind=True, name="app.tasks.tasks.process_document")
def process_document_task(self, document_id: int):
    """
    Background task to process a document.
    
    Args:
        document_id: ID of the document to process
    """
    db = SessionLocal()
    try:
        # Get document from database
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise Exception(f"Document {document_id} not found")
        
        # Update task status
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 0, "total": 100, "status": "Starting processing..."}
        )
        
        # Update document status
        document.processing_status = "processing"
        db.commit()
        
        # Log processing start
        log = ProcessingLog(
            document_id=document_id,
            log_level="INFO",
            message="Document processing started",
            step="initialization"
        )
        db.add(log)
        db.commit()
        
        # Process document
        file_path = Path(document.file_path)
        if not file_path.exists():
            raise Exception(f"Document file not found: {file_path}")
        
        # Update progress
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 25, "total": 100, "status": "Extracting text with Docling..."}
        )
        
        # Process with document processor
        processing_result = document_processor.process_document(file_path)
        
        # Update progress
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 50, "total": 100, "status": "Classifying document..."}
        )
        
        # Update document with processing results
        document.ocr_text = processing_result.get("ocr_text", "")
        document.structured_data = processing_result.get("docling_result", {})
        
        # Classify document type
        docling_result = processing_result.get("docling_result", {})
        text_content = docling_result.get("text_content", "")
        structured_data = docling_result.get("structured_data", {})
        
        document.document_type = document_processor.classify_document_type(text_content, structured_data)
        
        # Extract fund information
        fund_info = document_processor.extract_fund_information(text_content)
        document.fund_name = fund_info.get("fund_name")
        document.fund_id = fund_info.get("fund_id")
        
        # Update progress
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 75, "total": 100, "status": "Extracting structured data..."}
        )
        
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
        
        # Update progress
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 100, "total": 100, "status": "Finalizing..."}
        )
        
        # Mark as completed
        document.processing_status = "completed"
        document.processed_at = datetime.utcnow()
        db.commit()
        
        # Log completion
        log = ProcessingLog(
            document_id=document_id,
            log_level="INFO",
            message="Document processing completed successfully",
            step="completion"
        )
        db.add(log)
        db.commit()
        
        return {
            "status": "completed",
            "document_id": document_id,
            "document_type": document.document_type,
            "message": "Document processed successfully"
        }
        
    except Exception as e:
        # Update document status to failed
        if 'document' in locals():
            document.processing_status = "failed"
            db.commit()
        
        # Log error
        log = ProcessingLog(
            document_id=document_id,
            log_level="ERROR",
            message=f"Processing failed: {str(e)}",
            step="error"
        )
        db.add(log)
        db.commit()
        
        # Update task status
        current_task.update_state(
            state="FAILURE",
            meta={"error": str(e)}
        )
        
        raise Exception(f"Document processing failed: {str(e)}")
        
    finally:
        db.close()


@celery_app.task(name="app.tasks.tasks.process_pending_documents")
def process_pending_documents():
    """
    Background task to process all pending documents.
    """
    db = SessionLocal()
    try:
        # Get pending documents
        pending_documents = db.query(Document).filter(
            Document.processing_status == "pending"
        ).limit(5).all()  # Process up to 5 documents at a time
        
        processed_count = 0
        for document in pending_documents:
            try:
                # Queue document for processing
                process_document_task.delay(document.id)
                processed_count += 1
            except Exception as e:
                # Log error but continue with other documents
                log = ProcessingLog(
                    document_id=document.id,
                    log_level="ERROR",
                    message=f"Failed to queue document: {str(e)}",
                    step="queue"
                )
                db.add(log)
        
        db.commit()
        
        return {
            "status": "completed",
            "processed_count": processed_count,
            "message": f"Queued {processed_count} documents for processing"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to process pending documents: {str(e)}"
        }
        
    finally:
        db.close()


@celery_app.task(name="app.tasks.tasks.cleanup_old_files")
def cleanup_old_files():
    """
    Background task to cleanup old temporary files.
    """
    try:
        upload_dir = Path(settings.upload_dir)
        if not upload_dir.exists():
            return {"status": "skipped", "message": "Upload directory does not exist"}
        
        # Delete files older than 7 days
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        deleted_count = 0
        
        for file_path in upload_dir.iterdir():
            if file_path.is_file():
                file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_mtime < cutoff_date:
                    try:
                        file_path.unlink()
                        deleted_count += 1
                    except Exception as e:
                        # Log error but continue
                        print(f"Failed to delete {file_path}: {e}")
        
        return {
            "status": "completed",
            "deleted_count": deleted_count,
            "message": f"Deleted {deleted_count} old files"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to cleanup old files: {str(e)}"
        }


@celery_app.task(name="app.tasks.tasks.health_check")
def health_check_task():
    """
    Background task for health monitoring.
    """
    try:
        db = SessionLocal()
        
        # Check database connection
        db.execute("SELECT 1")
        
        # Check pending documents count
        pending_count = db.query(Document).filter(
            Document.processing_status == "pending"
        ).count()
        
        # Check failed documents count
        failed_count = db.query(Document).filter(
            Document.processing_status == "failed"
        ).count()
        
        db.close()
        
        return {
            "status": "healthy",
            "database": "connected",
            "pending_documents": pending_count,
            "failed_documents": failed_count,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
