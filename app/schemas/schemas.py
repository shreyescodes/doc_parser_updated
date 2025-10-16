"""
Pydantic schemas for API request/response models.
"""
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    """Enum for document types."""
    CAPITAL_CALL = "capital_call"
    DISTRIBUTION = "distribution"
    OTHER = "other"


class ProcessingStatus(str, Enum):
    """Enum for processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Document schemas
class DocumentBase(BaseModel):
    filename: str
    document_type: Optional[DocumentType] = None
    fund_name: Optional[str] = None
    fund_id: Optional[str] = None


class DocumentCreate(DocumentBase):
    pass


class DocumentResponse(DocumentBase):
    id: int
    original_filename: str
    file_size: int
    mime_type: str
    processing_status: ProcessingStatus
    extraction_confidence: Optional[float] = None
    uploaded_by_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class DocumentDetailResponse(DocumentResponse):
    ocr_text: Optional[str] = None
    structured_data: Optional[Dict[str, Any]] = None


# Capital Call schemas
class CapitalCallDetailBase(BaseModel):
    call_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    call_amount: Optional[float] = None
    currency: Optional[str] = None
    call_percentage: Optional[float] = None
    fund_name: Optional[str] = None
    fund_size: Optional[float] = None
    investment_period: Optional[str] = None
    lp_name: Optional[str] = None
    lp_commitment: Optional[float] = None
    lp_contribution_to_date: Optional[float] = None
    remaining_commitment: Optional[float] = None
    payment_instructions: Optional[str] = None
    wire_transfer_info: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class CapitalCallDetailCreate(CapitalCallDetailBase):
    document_id: int


class CapitalCallDetailResponse(CapitalCallDetailBase):
    id: int
    document_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Distribution schemas
class DistributionDetailBase(BaseModel):
    distribution_date: Optional[datetime] = None
    record_date: Optional[datetime] = None
    distribution_amount: Optional[float] = None
    currency: Optional[str] = None
    distribution_per_unit: Optional[float] = None
    fund_name: Optional[str] = None
    fund_nav: Optional[float] = None
    total_distributions: Optional[float] = None
    lp_name: Optional[str] = None
    lp_units: Optional[float] = None
    lp_distribution_amount: Optional[float] = None
    investment_period: Optional[str] = None
    irr: Optional[float] = None
    multiple: Optional[float] = None
    payment_method: Optional[str] = None
    payment_instructions: Optional[str] = None
    notes: Optional[str] = None


class DistributionDetailCreate(DistributionDetailBase):
    document_id: int


class DistributionDetailResponse(DistributionDetailBase):
    id: int
    document_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Processing schemas
class ProcessingLogResponse(BaseModel):
    id: int
    document_id: int
    log_level: str
    message: str
    step: Optional[str] = None
    processing_time: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Upload schemas
class UploadResponse(BaseModel):
    document_id: int
    message: str
    processing_status: ProcessingStatus


# Search schemas
class DocumentSearchRequest(BaseModel):
    query: Optional[str] = None
    document_type: Optional[DocumentType] = None
    fund_name: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    limit: int = 50
    offset: int = 0


class DocumentSearchResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int
    limit: int
    offset: int


# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# Template schemas
class DocumentTemplateBase(BaseModel):
    name: str
    document_type: DocumentType
    fund_name: Optional[str] = None
    extraction_rules: Dict[str, Any]
    field_mappings: Dict[str, Any]
    validation_rules: Optional[Dict[str, Any]] = None


class DocumentTemplateCreate(DocumentTemplateBase):
    pass


class DocumentTemplateResponse(DocumentTemplateBase):
    id: int
    is_active: bool
    created_by_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Health check schema
class HealthCheckResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    database_status: str
    redis_status: str
