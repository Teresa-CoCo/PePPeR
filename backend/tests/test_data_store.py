"""Tests for data store service."""

import json
import os
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from app.models.paper import Paper, PaperMetadata, Author, AIAnalysis
from app.services.data_store import DataStore


class TestDataStore:
    """Tests for DataStore class."""

    @pytest.fixture
    def data_store(self, temp_data_dir):
        """Create data store with temp directory."""
        with patch('app.services.data_store.settings') as mock_settings:
            mock_settings.PAPERS_JSON = temp_data_dir / "papers.json"
            mock_settings.DATA_DIR = temp_data_dir / "data"
            mock_settings.PAPERS_DIR = temp_data_dir / "papers"

            # Ensure directories exist
            mock_settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
            mock_settings.PAPERS_DIR.mkdir(parents=True, exist_ok=True)

            store = DataStore()
            yield store
            # Cleanup handled by temp_data_dir fixture

    def test_init_creates_file(self, data_store, temp_data_dir):
        """Test DataStore creates file on init."""
        assert temp_data_dir.joinpath("papers.json").exists()

    def test_add_paper(self, data_store, sample_paper):
        """Test adding a paper."""
        result = data_store.add_paper(sample_paper)
        assert result is True
        assert data_store.get_paper("test-1234.5678") == sample_paper

    def test_add_duplicate_paper(self, data_store, sample_paper):
        """Test adding duplicate paper returns False."""
        data_store.add_paper(sample_paper)
        result = data_store.add_paper(sample_paper)
        assert result is False

    def test_get_paper_not_found(self, data_store):
        """Test getting non-existent paper returns None."""
        assert data_store.get_paper("nonexistent") is None

    def test_update_paper(self, data_store, sample_paper):
        """Test updating a paper."""
        data_store.add_paper(sample_paper)

        updated = data_store.update_paper("test-1234.5678", {"processed": False})

        assert updated is not None
        assert updated.processed is False

    def test_update_paper_not_found(self, data_store):
        """Test updating non-existent paper returns None."""
        result = data_store.update_paper("nonexistent", {"processed": True})
        assert result is None

    def test_delete_paper(self, data_store, sample_paper):
        """Test deleting a paper."""
        data_store.add_paper(sample_paper)
        result = data_store.delete_paper("test-1234.5678")
        assert result is True
        assert data_store.get_paper("test-1234.5678") is None

    def test_delete_paper_not_found(self, data_store):
        """Test deleting non-existent paper returns False."""
        result = data_store.delete_paper("nonexistent")
        assert result is False

    def test_list_papers_empty(self, data_store):
        """Test listing papers when empty."""
        papers = data_store.list_papers()
        assert papers == []

    def test_list_papers(self, data_store, sample_paper):
        """Test listing all papers."""
        data_store.add_paper(sample_paper)
        papers = data_store.list_papers()
        assert len(papers) == 1

    def test_list_papers_by_category(self, data_store, sample_paper):
        """Test filtering papers by category."""
        data_store.add_paper(sample_paper)

        papers = data_store.list_papers(category="cs.AI")
        assert len(papers) == 1

        papers = data_store.list_papers(category="cs.CV")
        assert len(papers) == 0

    def test_list_papers_by_processed(self, data_store, sample_paper):
        """Test filtering papers by processed status."""
        data_store.add_paper(sample_paper)

        papers = data_store.list_papers(processed=True)
        assert len(papers) == 1

        papers = data_store.list_papers(processed=False)
        assert len(papers) == 0

    def test_list_papers_search(self, data_store, sample_paper):
        """Test searching papers by title/abstract."""
        data_store.add_paper(sample_paper)

        papers = data_store.list_papers(search="Test Paper")
        assert len(papers) == 1

        papers = data_store.list_papers(search="nonexistent")
        assert len(papers) == 0

    def test_list_papers_pagination(self, data_store):
        """Test pagination of paper listing."""
        for i in range(10):
            paper = Paper(
                metadata=PaperMetadata(
                    arxiv_id=f"test-{i:04d}",
                    title=f"Paper {i}",
                    authors=[],
                    abstract="Abstract",
                    published_date=datetime.now(),
                    pdf_url=f"http://test.com/{i}.pdf",
                    primary_category="cs.AI"
                )
            )
            data_store.add_paper(paper)

        papers = data_store.list_papers(limit=5, offset=0)
        assert len(papers) == 5

        papers = data_store.list_papers(limit=5, offset=5)
        assert len(papers) == 5

    def test_list_papers_sort_by_date(self, data_store):
        """Test papers are sorted by date (newest first)."""
        dates = [
            datetime(2024, 1, 10),
            datetime(2024, 1, 20),
            datetime(2024, 1, 15)
        ]

        for i, date in enumerate(dates):
            paper = Paper(
                metadata=PaperMetadata(
                    arxiv_id=f"test-sort-{i}",
                    title=f"Paper {i}",
                    authors=[],
                    abstract="Abstract",
                    published_date=date,
                    pdf_url=f"http://test.com/sort-{i}.pdf",
                    primary_category="cs.AI"
                )
            )
            data_store.add_paper(paper)

        papers = data_store.list_papers()
        assert len(papers) == 3
        assert papers[0].metadata.published_date == datetime(2024, 1, 20)
        assert papers[2].metadata.published_date == datetime(2024, 1, 10)

    def test_count_papers(self, data_store, sample_paper):
        """Test counting papers."""
        data_store.add_paper(sample_paper)
        assert data_store.count_papers() == 1

    def test_set_ai_analysis(self, data_store, sample_paper):
        """Test setting AI analysis for a paper."""
        data_store.add_paper(sample_paper)

        analysis = AIAnalysis(
            summary="New summary",
            key_findings=["New finding"],
            relevance_score=0.9
        )

        result = data_store.set_ai_analysis("test-1234.5678", analysis)
        assert result is True

        paper = data_store.get_paper("test-1234.5678")
        assert paper.ai_analysis.summary == "New summary"

    def test_add_chat_message(self, data_store, sample_paper):
        """Test adding chat message to paper."""
        from app.models.paper import ChatMessage

        data_store.add_paper(sample_paper)

        message = ChatMessage(role="user", content="Test message")
        result = data_store.add_chat_message("test-1234.5678", message)

        assert result is True

        paper = data_store.get_paper("test-1234.5678")
        assert len(paper.chat_history) == 1
        assert paper.chat_history[0].content == "Test message"

    def test_clear_chat_history(self, data_store, sample_paper):
        """Test clearing chat history."""
        from app.models.paper import ChatMessage

        data_store.add_paper(sample_paper)

        # Add messages
        data_store.add_chat_message("test-1234.5678", ChatMessage(role="user", content="Msg1"))
        data_store.add_chat_message("test-1234.5678", ChatMessage(role="assistant", content="Reply1"))

        result = data_store.clear_chat_history("test-1234.5678")
        assert result is True

        paper = data_store.get_paper("test-1234.5678")
        assert len(paper.chat_history) == 0

    def test_get_chat_history(self, data_store, sample_paper):
        """Test getting chat history."""
        from app.models.paper import ChatMessage

        data_store.add_paper(sample_paper)

        data_store.add_chat_message("test-1234.5678", ChatMessage(role="user", content="Msg1"))

        history = data_store.get_chat_history("test-1234.5678")
        assert len(history) == 1

    def test_set_extracted_text(self, data_store, sample_paper):
        """Test setting extracted text for a paper."""
        data_store.add_paper(sample_paper)

        result = data_store.set_extracted_text("test-1234.5678", "New extracted text")
        assert result is True

        paper = data_store.get_paper("test-1234.5678")
        assert paper.extracted_text == "New extracted text"

    def test_set_processed(self, data_store, sample_paper):
        """Test setting processed status."""
        data_store.add_paper(sample_paper)

        result = data_store.set_processed("test-1234.5678", True)
        assert result is True

        paper = data_store.get_paper("test-1234.5678")
        assert paper.processed is True

    def test_clear_all(self, data_store, sample_paper):
        """Test clearing all papers."""
        data_store.add_paper(sample_paper)

        count = data_store.clear_all()
        assert count == 1
        assert data_store.count_papers() == 0

    def test_reload(self, data_store, sample_paper):
        """Test reloading data from file."""
        data_store.add_paper(sample_paper)
        data_store._papers_cache.clear()

        data_store.reload()

        paper = data_store.get_paper("test-1234.5678")
        assert paper is not None
        assert paper.metadata.title == "Test Paper Title"
