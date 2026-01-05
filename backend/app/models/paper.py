"""Paper data models."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class Author(BaseModel):
    """Paper author model."""

    name: str
    arxiv_id: Optional[str] = None


class PaperMetadata(BaseModel):
    """Metadata for a paper from arXiv."""

    arxiv_id: str
    title: str
    authors: List[Author]
    abstract: str
    published_date: datetime
    updated_date: Optional[datetime] = None
    pdf_url: str
    primary_category: str
    categories: List[str] = Field(default_factory=list)
    comment: Optional[str] = None
    journal_ref: Optional[str] = None
    doi: Optional[str] = None


class AIAnalysis(BaseModel):
    """AI-generated analysis of a paper."""

    summary: str = ""
    key_findings: List[str] = Field(default_factory=list)
    methodology: Optional[str] = None
    strengths: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    relevance_score: Optional[float] = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class ChatMessage(BaseModel):
    """Chat message model."""

    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Paper(BaseModel):
    """Complete paper model with all associated data."""

    metadata: PaperMetadata
    pdf_path: Optional[str] = None
    extracted_text: Optional[str] = None
    ai_analysis: Optional[AIAnalysis] = None
    chat_history: List[ChatMessage] = Field(default_factory=list)
    processed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
