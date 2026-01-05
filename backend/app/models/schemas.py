"""Pydantic schemas for API requests and responses."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class AuthorSchema(BaseModel):
    """Author schema for responses."""

    name: str
    arxiv_id: Optional[str] = None


class PaperMetadataSchema(BaseModel):
    """Paper metadata schema for responses."""

    arxiv_id: str
    title: str
    authors: List[AuthorSchema]
    abstract: str
    published_date: datetime
    pdf_url: str
    primary_category: str
    categories: List[str]
    comment: Optional[str] = None
    journal_ref: Optional[str] = None
    doi: Optional[str] = None


class AIAnalysisSchema(BaseModel):
    """AI analysis schema for responses."""

    summary: str
    key_findings: List[str] = Field(default_factory=list)
    methodology: Optional[str] = None
    strengths: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    relevance_score: Optional[float] = None
    generated_at: datetime


class ChatMessageSchema(BaseModel):
    """Chat message schema."""

    role: str
    content: str
    timestamp: datetime


class PaperResponse(BaseModel):
    """Response schema for paper list items."""

    arxiv_id: str
    title: str
    authors: List[str]
    abstract: str
    published_date: datetime
    category: str
    ai_summary: Optional[str] = None
    processed: bool = False


class PaperDetailResponse(BaseModel):
    """Response schema for detailed paper view."""

    metadata: PaperMetadataSchema
    pdf_path: Optional[str] = None
    extracted_text: Optional[str] = None
    ai_analysis: Optional[AIAnalysisSchema] = None
    chat_history: List[ChatMessageSchema] = Field(default_factory=list)
    processed: bool = False


class FetchRequest(BaseModel):
    """Request schema for fetching papers."""

    category: str
    date: Optional[str] = None  # YYYY-MM-DD format


class FetchResponse(BaseModel):
    """Response schema for fetch operation."""

    category: str
    date: str
    papers_found: int
    papers_downloaded: int
    papers: List[PaperResponse]


class ProcessRequest(BaseModel):
    """Request schema for processing a paper."""

    skip_ocr: bool = False


class ProcessResponse(BaseModel):
    """Response schema for processing operation."""

    arxiv_id: str
    ocr_success: bool
    text_extracted: bool
    ai_analysis_generated: bool
    message: str


class ChatRequest(BaseModel):
    """Request schema for chat messages."""

    message: str
    model: Optional[str] = None


class ChatResponse(BaseModel):
    """Response schema for chat (non-streaming)."""

    response: str
    message_id: str


class SchedulerConfigRequest(BaseModel):
    """Request schema for scheduler configuration."""

    enabled: bool
    time: str  # HH:MM format
    categories: List[str]


class SchedulerConfigResponse(BaseModel):
    """Response schema for scheduler configuration."""

    enabled: bool
    time: str
    categories: List[str]
