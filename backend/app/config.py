"""Configuration and settings management."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Configuration
    OPENROUTER_API_KEY: str = Field(default="", description="OpenRouter API key")
    OPENROUTER_DEFAULT_MODEL: str = Field(
        default="anthropic/claude-3.5-sonnet",
        description="Default LLM model for completions"
    )

    # PaddleOCR Configuration
    PADDLEOCR_API_URL: str = Field(
        default="https://aip.baidubce.com/paddle/ocr/v3/recognize",
        description="PaddleOCR API endpoint"
    )
    PADDLEOCR_TOKEN: str = Field(default="", description="PaddleOCR access token")

    # ArXiv Configuration
    ARXIV_DELAY_SECONDS: float = Field(default=3.0, description="Delay between arXiv requests")
    ARXIV_MAX_RESULTS: int = Field(default=50, description="Maximum results per request")

    # Paths
    PAPERS_DIR: Path = Field(default=Path("./papers"), description="Directory for PDF storage")
    DATA_DIR: Path = Field(default=Path("./data"), description="Directory for data files")
    PAPERS_JSON: Path = Field(
        default=Path("./data/papers.json"),
        description="Papers database file"
    )

    # Scheduler
    SCHEDULER_ENABLED: bool = Field(default=False, description="Enable/disable scheduler")
    SCHEDULER_TIME: str = Field(default="08:00", description="Daily fetch time (HH:MM)")
    SCHEDULER_CATEGORIES: str = Field(
        default="cs.AI,cs.LG,cs.CL",
        description="Categories to fetch"
    )

    # Server
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")
    DEBUG: bool = Field(default=False, description="Debug mode")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def ensure_directories() -> None:
    """Ensure required directories exist."""
    settings.PAPERS_DIR.mkdir(parents=True, exist_ok=True)
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
