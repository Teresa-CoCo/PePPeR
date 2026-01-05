"""Pytest configuration and fixtures."""

import sys
from pathlib import Path

import pytest

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set test environment
import os
os.environ.setdefault("OPENROUTER_API_KEY", "test-api-key")
os.environ.setdefault("SCHEDULER_ENABLED", "false")


@pytest.fixture
def sample_paper_metadata():
    """Sample paper metadata for testing."""
    from datetime import datetime
    from app.models.paper import PaperMetadata, Author

    return PaperMetadata(
        arxiv_id="test-1234.5678",
        title="Test Paper Title",
        authors=[Author(name="Test Author", arxiv_id="testauthor1")],
        abstract="This is a test abstract for the paper.",
        published_date=datetime(2024, 1, 15),
        updated_date=datetime(2024, 1, 20),
        pdf_url="http://arxiv.org/pdf/test-1234.5678.pdf",
        primary_category="cs.AI",
        categories=["cs.AI", "cs.LG"],
        comment="Test comment",
        journal_ref="Test Journal Ref",
        doi="10.1234/test.doi"
    )


@pytest.fixture
def sample_ai_analysis():
    """Sample AI analysis for testing."""
    from datetime import datetime
    from app.models.paper import AIAnalysis

    return AIAnalysis(
        summary="Test summary",
        key_findings=["Finding 1", "Finding 2"],
        methodology="Test methodology",
        strengths=["Strength 1"],
        limitations=["Limitation 1"],
        relevance_score=0.85,
        generated_at=datetime.utcnow()
    )


@pytest.fixture
def sample_paper(sample_paper_metadata, sample_ai_analysis):
    """Sample paper for testing."""
    from app.models.paper import Paper

    return Paper(
        metadata=sample_paper_metadata,
        pdf_path="papers/test-1234.5678.pdf",
        extracted_text="Extracted text content",
        ai_analysis=sample_ai_analysis,
        processed=True
    )


@pytest.fixture
def sample_chat_message():
    """Sample chat message for testing."""
    from app.models.paper import ChatMessage

    return ChatMessage(
        role="user",
        content="What is the main contribution?"
    )


@pytest.fixture
def temp_data_dir(tmp_path):
    """Temporary data directory for testing."""
    data_dir = tmp_path / "data"
    papers_dir = tmp_path / "papers"
    data_dir.mkdir()
    papers_dir.mkdir()
    return tmp_path
