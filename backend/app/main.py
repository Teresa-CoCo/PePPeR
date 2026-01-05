"""Main FastAPI application."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings, ensure_directories
from app.api.routes import papers_router, chat_router
from app.utils.scheduler import scheduler_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info("Starting PePPeR application...")
    ensure_directories()

    if settings.SCHEDULER_ENABLED:
        scheduler_service.start()

    yield

    # Shutdown
    logger.info("Shutting down PePPeR application...")
    if scheduler_service.is_running():
        scheduler_service.stop()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="PePPeR - Intelligent ArXiv Research Assistant",
        description="Fetch, analyze, and chat with arXiv papers using AI",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(papers_router, prefix="/api/papers", tags=["papers"])
    app.include_router(chat_router, prefix="/api/chat", tags=["chat"])

    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "name": "PePPeR",
            "version": "0.1.0",
            "description": "Intelligent ArXiv Research Assistant",
        }

    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "healthy"}

    return app


# Create the application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
