"""API routes package."""

from app.api.routes.papers import router as papers_router
from app.api.routes.chat import router as chat_router

__all__ = ["papers_router", "chat_router"]
