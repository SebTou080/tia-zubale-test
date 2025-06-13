from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class ProductIngest(BaseModel):
    """Schema for product ingestion"""
    name: str = Field(..., min_length=1, description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    category: Optional[str] = Field(None, description="Product category")
    price: Optional[float] = Field(None, gt=0, description="Product price")
    stock_quantity: Optional[int] = Field(None, ge=0, description="Stock quantity")
    specs: Optional[Dict[str, Any]] = Field(None, description="Product specifications")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional product metadata")


class ChatMessage(BaseModel):
    """Schema for individual chat messages"""
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class QueryRequest(BaseModel):
    """Schema for query requests"""
    query: str = Field(..., min_length=1, description="User query")
    conversation_history: Optional[List[ChatMessage]] = Field(None, description="Previous conversation messages")


class DocumentReference(BaseModel):
    """Schema for document references in responses"""
    product_id: str
    product_name: str
    relevance_score: float
    content_snippet: str


class QueryResponse(BaseModel):
    """Schema for query responses"""
    query: str
    answer: str
    sources: List[DocumentReference]
    confidence_score: float
    processing_time_ms: int
    conversation_history: List[ChatMessage]


class IngestResponse(BaseModel):
    """Schema for ingestion responses"""
    product_id: str
    message: str
    status: str


class HealthResponse(BaseModel):
    """Schema for health check responses"""
    status: str
    timestamp: datetime
    version: str 