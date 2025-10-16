"""
Document models for the LP Document Parser.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
from datetime import datetime
from typing import Optional, Dict, Any


class Document(Base):
    """Main document model for storing document metadata."""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    
    # Document classification
    document_type = Column(String(50), nullable=True)  # capital_call, distribution, other
    fund_name = Column(String(255), nullable=True)
    fund_id = Column(String(100), nullable=True)
    
    # Processing status
    processing_status = Column(String(20), default="pending")  # pending, processing, completed, failed
    ocr_text = Column(Text, nullable=True)
    structured_data = Column(JSON, nullable=True)
    extraction_confidence = Column(Float, nullable=True)
    
    # Metadata
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships - will be added after proper model setup
    # uploaded_by = relationship("User", back_populates="documents")
    capital_call_details = relationship("CapitalCallDetail", back_populates="document", uselist=False)
    distribution_details = relationship("DistributionDetail", back_populates="document", uselist=False)


class CapitalCallDetail(Base):
    """Specific details extracted from capital call notices."""
    __tablename__ = "capital_call_details"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, unique=True)
    
    # Capital call specific fields
    call_date = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=True)
    call_amount = Column(Float, nullable=True)
    currency = Column(String(3), nullable=True)
    call_percentage = Column(Float, nullable=True)
    
    # Fund information
    fund_name = Column(String(255), nullable=True)
    fund_size = Column(Float, nullable=True)
    investment_period = Column(String(100), nullable=True)
    
    # LP information
    lp_name = Column(String(255), nullable=True)
    lp_commitment = Column(Float, nullable=True)
    lp_contribution_to_date = Column(Float, nullable=True)
    remaining_commitment = Column(Float, nullable=True)
    
    # Payment details
    payment_instructions = Column(Text, nullable=True)
    wire_transfer_info = Column(JSON, nullable=True)
    
    # Additional data
    notes = Column(Text, nullable=True)
    extracted_data = Column(JSON, nullable=True)  # Raw extracted data for reference
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="capital_call_details")


class DistributionDetail(Base):
    """Specific details extracted from distribution notices."""
    __tablename__ = "distribution_details"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, unique=True)
    
    # Distribution specific fields
    distribution_date = Column(DateTime, nullable=True)
    record_date = Column(DateTime, nullable=True)
    distribution_amount = Column(Float, nullable=True)
    currency = Column(String(3), nullable=True)
    distribution_per_unit = Column(Float, nullable=True)
    
    # Fund information
    fund_name = Column(String(255), nullable=True)
    fund_nav = Column(Float, nullable=True)
    total_distributions = Column(Float, nullable=True)
    
    # LP information
    lp_name = Column(String(255), nullable=True)
    lp_units = Column(Float, nullable=True)
    lp_distribution_amount = Column(Float, nullable=True)
    
    # Investment details
    investment_period = Column(String(100), nullable=True)
    irr = Column(Float, nullable=True)  # Internal Rate of Return
    multiple = Column(Float, nullable=True)  # Investment multiple
    
    # Payment details
    payment_method = Column(String(50), nullable=True)
    payment_instructions = Column(Text, nullable=True)
    
    # Additional data
    notes = Column(Text, nullable=True)
    extracted_data = Column(JSON, nullable=True)  # Raw extracted data for reference
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="distribution_details")


class ProcessingLog(Base):
    """Log of document processing activities."""
    __tablename__ = "processing_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    
    # Log details
    log_level = Column(String(20), nullable=False)  # INFO, WARNING, ERROR
    message = Column(Text, nullable=False)
    step = Column(String(100), nullable=True)  # ocr, classification, extraction, etc.
    processing_time = Column(Float, nullable=True)  # Time taken in seconds
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    document = relationship("Document")


class DocumentTemplate(Base):
    """Templates for different types of LP documents."""
    __tablename__ = "document_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    document_type = Column(String(50), nullable=False)
    fund_name = Column(String(255), nullable=True)
    
    # Template configuration
    extraction_rules = Column(JSON, nullable=False)
    field_mappings = Column(JSON, nullable=False)
    validation_rules = Column(JSON, nullable=True)
    
    # Template metadata
    is_active = Column(Boolean, default=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    created_by = relationship("User")
