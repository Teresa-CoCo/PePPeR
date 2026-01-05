"""ArXiv API client service."""

import asyncio
import logging
import time
from datetime import date, datetime
from typing import List, Optional

from arxiv import Search, SortOrder, SortCriterion

from app.config import settings
from app.models.paper import PaperMetadata, Author

logger = logging.getLogger(__name__)


class ArxivClient:
    """Client for fetching papers from arXiv."""

    def __init__(self):
        """Initialize the arXiv client."""
        self.delay = settings.ARXIV_DELAY_SECONDS
        self.max_results = settings.ARXIV_MAX_RESULTS
        self._last_request_time: float = 0

    def _rate_limit(self) -> None:
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.delay:
            asyncio.sleep(self.delay - elapsed)
        self._last_request_time = time.time()

    def _to_datetime(self, arxiv_date) -> datetime:
        """Convert arXiv date to datetime."""
        if isinstance(arxiv_date, datetime):
            return arxiv_date
        if isinstance(arxiv_date, date):
            return datetime.combine(arxiv_date, datetime.min.time())
        return datetime.now()

    def _parse_entry(self, entry) -> PaperMetadata:
        """Parse an arXiv entry into PaperMetadata."""
        # Extract arxiv_id without version
        arxiv_id = entry.id.split("/abs/")[-1]
        if "/v" in arxiv_id:
            arxiv_id = arxiv_id.split("/v")[0]

        # Parse authors
        authors = [
            Author(name=a.name, arxiv_id=getattr(a, "arxiv_id", None))
            for a in entry.authors
        ]

        return PaperMetadata(
            arxiv_id=arxiv_id,
            title=entry.title.strip(),
            authors=authors,
            abstract=entry.summary.strip(),
            published_date=self._to_datetime(entry.published),
            updated_date=self._to_datetime(entry.updated) if entry.updated else None,
            pdf_url=entry.pdf_url,
            primary_category=entry.primary_category,
            categories=list(entry.categories),
            comment=getattr(entry, "comment", None),
            journal_ref=getattr(entry, "journal_ref", None),
            doi=getattr(entry, "doi", None),
        )

    def _build_date_query(self, target_date: Optional[date] = None) -> str:
        """Build arXiv date query for a specific date."""
        if target_date is None:
            target_date = date.today()

        date_str = target_date.strftime("%Y%m%d")
        # Query for papers submitted on the specific date
        return f"submittedDate:[{date_str} TO {date_str}]"

    def fetch_by_category(
        self,
        category: str,
        target_date: Optional[date] = None,
    ) -> List[PaperMetadata]:
        """
        Fetch papers for a specific category and date.

        Args:
            category: arXiv category (e.g., "cs.AI", "cs.LG")
            target_date: Date to fetch papers for (defaults to today)

        Returns:
            List of PaperMetadata objects
        """
        self._rate_limit()

        date_query = self._build_date_query(target_date)
        query = f"cat:{category} AND {date_query}"

        logger.info(f"Fetching papers with query: {query}")

        try:
            search = Search(
                query=query,
                max_results=self.max_results,
                sort_by=SortCriterion.SubmittedDate,
                sort_order=SortOrder.Descending,
            )

            papers = []
            for entry in search.entries():
                papers.append(self._parse_entry(entry))

            logger.info(f"Found {len(papers)} papers in {category} for date {target_date}")
            return papers

        except Exception as e:
            logger.error(f"Error fetching papers from arXiv: {e}")
            raise

    async def fetch_by_category_async(
        self,
        category: str,
        target_date: Optional[date] = None,
    ) -> List[PaperMetadata]:
        """Async wrapper for fetch_by_category."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.fetch_by_category, category, target_date)


# Singleton instance
arxiv_client = ArxivClient()
