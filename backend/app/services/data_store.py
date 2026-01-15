"""Data persistence layer using JSON file storage."""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

from app.config import settings
from app.models.paper import Paper, AIAnalysis, ChatMessage

logger = logging.getLogger(__name__)


class DataStore:
    """JSON file-based data store for papers and metadata."""

    def __init__(self):
        """Initialize data store."""
        self.papers_file = settings.PAPERS_JSON
        self._papers_cache: Dict[str, Paper] = {}
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Create data file if it doesn't exist."""
        if not self.papers_file.exists():
            self._save_to_file({})
        else:
            self._load_cache()

    def _load_cache(self) -> None:
        """Load papers from file into memory cache."""
        try:
            with open(self.papers_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for arxiv_id, paper_data in data.items():
                    self._papers_cache[arxiv_id] = Paper.model_validate(paper_data)
            logger.info(f"Loaded {len(self._papers_cache)} papers from cache")
        except Exception as e:
            logger.error(f"Failed to load papers cache: {e}")
            self._papers_cache = {}

    def _save_to_file(self, data: dict) -> None:
        """Save data to JSON file."""
        self.papers_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.papers_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)

    def _save_cache(self) -> None:
        """Save cache to file."""
        data = {
            arxiv_id: paper.model_dump(mode="json")
            for arxiv_id, paper in self._papers_cache.items()
        }
        self._save_to_file(data)

    # Paper CRUD operations

    def add_paper(self, paper: Paper) -> bool:
        """
        Add a new paper to the store.

        Args:
            paper: Paper to add

        Returns:
            True if added, False if already exists
        """
        arxiv_id = paper.metadata.arxiv_id
        if arxiv_id in self._papers_cache:
            logger.debug(f"Paper {arxiv_id} already exists")
            return False

        self._papers_cache[arxiv_id] = paper
        self._save_cache()
        logger.info(f"Added paper: {arxiv_id}")
        return True

    def get_paper(self, arxiv_id: str) -> Optional[Paper]:
        """Get a paper by ID."""
        return self._papers_cache.get(arxiv_id)

    def update_paper(self, arxiv_id: str, updates: dict) -> Optional[Paper]:
        """
        Update a paper with new data.

        Args:
            arxiv_id: Paper ID
            updates: Dictionary of fields to update

        Returns:
            Updated paper or None if not found
        """
        paper = self._papers_cache.get(arxiv_id)
        if not paper:
            return None

        for key, value in updates.items():
            if hasattr(paper, key):
                setattr(paper, key, value)

        paper.updated_at = datetime.utcnow()
        self._save_cache()
        return paper

    def delete_paper(self, arxiv_id: str) -> bool:
        """Delete a paper from the store."""
        if arxiv_id in self._papers_cache:
            del self._papers_cache[arxiv_id]
            self._save_cache()
            logger.info(f"Deleted paper: {arxiv_id}")
            return True
        return False

    def list_papers(
        self,
        category: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        processed: Optional[bool] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Paper]:
        """
        List papers with optional filters.

        Args:
            category: Filter by category
            date_from: Filter by start date (YYYY-MM-DD)
            date_to: Filter by end date (YYYY-MM-DD)
            processed: Filter by processed status
            search: Search in title and abstract
            limit: Maximum results
            offset: Pagination offset

        Returns:
            List of matching papers
        """
        papers = list(self._papers_cache.values())

        # Apply filters
        if category:
            papers = [p for p in papers if p.metadata.primary_category == category]

        if date_from:
            from_dt = datetime.fromisoformat(date_from)
            papers = [p for p in papers if p.metadata.published_date >= from_dt]

        if date_to:
            to_dt = datetime.fromisoformat(date_to)
            papers = [p for p in papers if p.metadata.published_date <= to_dt]

        if processed is not None:
            papers = [p for p in papers if p.processed == processed]

        if search:
            search_lower = search.lower()
            papers = [
                p
                for p in papers
                if search_lower in p.metadata.title.lower()
                or search_lower in p.metadata.abstract.lower()
            ]

        # Sort by date (newest first)
        papers.sort(key=lambda p: p.metadata.published_date, reverse=True)

        # Apply pagination
        return papers[offset : offset + limit]

    def count_papers(
        self,
        category: Optional[str] = None,
        processed: Optional[bool] = None,
    ) -> int:
        """Count papers matching filters."""
        papers = list(self._papers_cache.values())

        if category:
            papers = [p for p in papers if p.metadata.primary_category == category]

        if processed is not None:
            papers = [p for p in papers if p.processed == processed]

        return len(papers)

    # AI Analysis operations

    def set_ai_analysis(self, arxiv_id: str, analysis: AIAnalysis) -> bool:
        """Set AI analysis for a paper."""
        paper = self._papers_cache.get(arxiv_id)
        if not paper:
            return False

        paper.ai_analysis = analysis
        paper.updated_at = datetime.utcnow()
        self._save_cache()
        return True

    # Chat history operations

    def add_chat_message(self, arxiv_id: str, message: ChatMessage) -> bool:
        """Add a message to paper's chat history."""
        paper = self._papers_cache.get(arxiv_id)
        if not paper:
            return False

        paper.chat_history.append(message)
        paper.updated_at = datetime.utcnow()
        self._save_cache()
        return True

    def clear_chat_history(self, arxiv_id: str) -> bool:
        """Clear chat history for a paper."""
        paper = self._papers_cache.get(arxiv_id)
        if not paper:
            return False

        paper.chat_history = []
        paper.updated_at = datetime.utcnow()
        self._save_cache()
        return True

    def get_chat_history(self, arxiv_id: str) -> List[ChatMessage]:
        """Get chat history for a paper."""
        paper = self._papers_cache.get(arxiv_id)
        if not paper:
            return []
        return paper.chat_history

    # Text operations

    def set_extracted_text(self, arxiv_id: str, text: str) -> bool:
        """Set extracted text for a paper."""
        paper = self._papers_cache.get(arxiv_id)
        if not paper:
            return False

        paper.extracted_text = text
        paper.updated_at = datetime.utcnow()
        self._save_cache()
        return True

    def set_processed(self, arxiv_id: str, processed: bool = True) -> bool:
        """Mark a paper as processed."""
        paper = self._papers_cache.get(arxiv_id)
        if not paper:
            return False

        paper.processed = processed
        paper.updated_at = datetime.utcnow()
        self._save_cache()
        return True

    # Utility

    def reload(self) -> None:
        """Reload data from file."""
        self._papers_cache.clear()
        self._load_cache()

    def clear_all(self) -> int:
        """Clear all data (for testing). Returns count of deleted papers."""
        count = len(self._papers_cache)
        self._papers_cache.clear()
        self._save_to_file({})
        logger.info(f"Cleared {count} papers from store")
        return count


# Singleton instance
data_store = DataStore()
