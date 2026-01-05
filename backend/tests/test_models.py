"""Tests for paper data models."""

from datetime import datetime

import pytest
from app.models.paper import (
    Author,
    PaperMetadata,
    AIAnalysis,
    ChatMessage,
    Paper
)


class TestAuthor:
    """Tests for Author model."""

    def test_author_creation(self):
        """Test basic author creation."""
        author = Author(name="John Doe", arxiv_id="johndoe1")
        assert author.name == "John Doe"
        assert author.arxiv_id == "johndoe1"

    def test_author_optional_arxiv_id(self):
        """Test author without arxiv_id."""
        author = Author(name="Jane Doe")
        assert author.arxiv_id is None


class TestPaperMetadata:
    """Tests for PaperMetadata model."""

    def test_metadata_creation(self, sample_paper_metadata):
        """Test basic metadata creation."""
        assert sample_paper_metadata.arxiv_id == "test-1234.5678"
        assert sample_paper_metadata.title == "Test Paper Title"
        assert len(sample_paper_metadata.authors) == 1
        assert sample_paper_metadata.primary_category == "cs.AI"

    def test_metadata_categories_default(self):
        """Test categories default to empty list."""
        metadata = PaperMetadata(
            arxiv_id="test-0001",
            title="Title",
            authors=[],
            abstract="Abstract",
            published_date=datetime.now(),
            pdf_url="http://test.com/pdf",
            primary_category="cs.AI"
        )
        assert metadata.categories == []

    def test_metadata_optional_fields(self):
        """Test optional fields can be None."""
        metadata = PaperMetadata(
            arxiv_id="test-0002",
            title="Title",
            authors=[],
            abstract="Abstract",
            published_date=datetime.now(),
            pdf_url="http://test.com/pdf",
            primary_category="cs.AI",
            comment=None,
            journal_ref=None,
            doi=None,
            updated_date=None
        )
        assert metadata.comment is None
        assert metadata.journal_ref is None
        assert metadata.doi is None


class TestAIAnalysis:
    """Tests for AIAnalysis model."""

    def test_analysis_creation(self, sample_ai_analysis):
        """Test basic analysis creation."""
        assert sample_ai_analysis.summary == "Test summary"
        assert len(sample_ai_analysis.key_findings) == 2
        assert sample_ai_analysis.relevance_score == 0.85

    def test_analysis_defaults(self):
        """Test analysis default values."""
        analysis = AIAnalysis(summary="Summary")
        assert analysis.summary == "Summary"
        assert analysis.key_findings == []
        assert analysis.strengths == []
        assert analysis.limitations == []
        assert analysis.relevance_score is None
        assert isinstance(analysis.generated_at, datetime)


class TestChatMessage:
    """Tests for ChatMessage model."""

    def test_chat_message_creation(self, sample_chat_message):
        """Test basic chat message creation."""
        assert sample_chat_message.role == "user"
        assert sample_chat_message.content == "What is the main contribution?"
        assert isinstance(sample_chat_message.timestamp, datetime)

    def test_chat_message_assistant(self):
        """Test assistant message creation."""
        message = ChatMessage(
            role="assistant",
            content="The main contribution is..."
        )
        assert message.role == "assistant"
        assert message.content.startswith("The main contribution")


class TestPaper:
    """Tests for Paper model."""

    def test_paper_creation(self, sample_paper, sample_paper_metadata):
        """Test basic paper creation."""
        assert sample_paper.metadata == sample_paper_metadata
        assert sample_paper.pdf_path == "papers/test-1234.5678.pdf"
        assert sample_paper.processed is True

    def test_paper_defaults(self, sample_paper_metadata):
        """Test paper default values."""
        paper = Paper(metadata=sample_paper_metadata)
        assert paper.pdf_path is None
        assert paper.extracted_text is None
        assert paper.ai_analysis is None
        assert paper.chat_history == []
        assert paper.processed is False
        assert isinstance(paper.created_at, datetime)
        assert paper.updated_at is None
