"""Models package."""

from app.models.paper import Paper, PaperMetadata, AIAnalysis, ChatMessage, Author
from app.models.schemas import (
    PaperResponse,
    PaperDetailResponse,
    FetchRequest,
    FetchResponse,
    ProcessRequest,
    ProcessResponse,
    ChatRequest,
    ChatResponse,
)

__all__ = [
    "Paper",
    "PaperMetadata",
    "AIAnalysis",
    "ChatMessage",
    "Author",
    "PaperResponse",
    "PaperDetailResponse",
    "FetchRequest",
    "FetchResponse",
    "ProcessRequest",
    "ProcessResponse",
    "ChatRequest",
    "ChatResponse",
]
