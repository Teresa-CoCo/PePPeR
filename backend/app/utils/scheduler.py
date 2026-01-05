"""Scheduler service for automatic paper fetching."""

import logging
from typing import List

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import settings
from app.services.arxiv_service import arxiv_client
from app.services.data_store import data_store
from app.services.pdf_service import pdf_service
from app.services.ocr_service import ocr_service
from app.services.llm_service import llm_service
from app.models.paper import Paper

logger = logging.getLogger(__name__)


class SchedulerService:
    """Service for scheduling automatic paper fetching."""

    def __init__(self):
        """Initialize scheduler service."""
        self.scheduler = AsyncIOScheduler()
        self._enabled = settings.SCHEDULER_ENABLED
        self._fetch_time = settings.SCHEDULER_TIME
        self._categories: List[str] = [
            c.strip() for c in settings.SCHEDULER_CATEGORIES.split(",")
        ]

    @property
    def enabled(self) -> bool:
        """Check if scheduler is enabled."""
        return self._enabled

    @property
    def fetch_time(self) -> str:
        """Get the configured fetch time."""
        return self._fetch_time

    @property
    def categories(self) -> List[str]:
        """Get the configured categories."""
        return self._categories

    def set_config(self, enabled: bool, time: str, categories: List[str]) -> None:
        """
        Update scheduler configuration.

        Args:
            enabled: Whether scheduler should run
            time: Time to run (HH:MM format)
            categories: List of categories to fetch
        """
        self._enabled = enabled
        self._fetch_time = time
        self._categories = categories

        if self.scheduler.running:
            self._restart()

    async def fetch_all_categories(self) -> dict:
        """
        Fetch papers for all configured categories.

        Returns:
            Dictionary with fetch results per category
        """
        results = {}

        for category in self._categories:
            try:
                result = await self._fetch_category(category)
                results[category] = result
            except Exception as e:
                logger.error(f"Error fetching category {category}: {e}")
                results[category] = {"error": str(e)}

        return results

    async def _fetch_category(self, category: str) -> dict:
        """Fetch papers for a single category."""
        # Fetch metadata from arXiv
        papers_data = arxiv_client.fetch_by_category(category)

        papers_downloaded = 0
        papers_saved = 0

        for metadata in papers_data:
            paper = Paper(metadata=metadata)

            # Download PDF
            pdf_path = await pdf_service.download_pdf(
                metadata.arxiv_id,
                metadata.pdf_url,
                metadata.primary_category,
                metadata.published_date,
            )

            if pdf_path:
                paper.pdf_path = pdf_path
                papers_downloaded += 1

            # Save to store
            if data_store.add_paper(paper):
                papers_saved += 1

        return {
            "found": len(papers_data),
            "downloaded": papers_downloaded,
            "saved": papers_saved,
        }

    async def process_all_papers(self) -> dict:
        """
        Process (OCR + AI analysis) all unprocessed papers.

        Returns:
            Dictionary with processing results
        """
        results = {"processed": 0, "failed": 0, "skipped": 0}

        papers = data_store.list_papers(processed=False)

        for paper in papers:
            if not paper.pdf_path:
                results["skipped"] += 1
                continue

            try:
                # OCR
                if not paper.extracted_text:
                    text = ocr_service.extract_text(paper.pdf_path)
                    if text:
                        data_store.set_extracted_text(paper.metadata.arxiv_id, text)

                # AI Analysis
                analysis = await llm_service.analyze_paper(
                    title=paper.metadata.title,
                    abstract=paper.metadata.abstract,
                    full_text=paper.extracted_text,
                )
                data_store.set_ai_analysis(paper.metadata.arxiv_id, analysis)
                data_store.set_processed(paper.metadata.arxiv_id, True)

                results["processed"] += 1

            except Exception as e:
                logger.error(f"Error processing paper {paper.metadata.arxiv_id}: {e}")
                results["failed"] += 1

        return results

    def _run_job(self):
        """Internal job that runs in the scheduler."""
        import asyncio

        async def wrapper():
            logger.info("Running scheduled paper fetch...")
            try:
                await self.fetch_all_categories()
                await self.process_all_papers()
                logger.info("Scheduled fetch completed")
            except Exception as e:
                logger.error(f"Scheduled fetch failed: {e}")

        asyncio.run(wrapper())

    def start(self) -> None:
        """Start the scheduler."""
        if not self._enabled:
            logger.info("Scheduler is disabled")
            return

        hour, minute = map(int, self._fetch_time.split(":"))

        self.scheduler.add_job(
            self._run_job,
            CronTrigger(hour=hour, minute=minute),
            id="daily_fetch",
            name="Daily paper fetch",
            replace_existing=True,
        )

        self.scheduler.start()
        logger.info(f"Scheduler started, will fetch at {self._fetch_time}")

    def stop(self) -> None:
        """Stop the scheduler."""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")

    def _restart(self) -> None:
        """Restart the scheduler with new configuration."""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
        self.scheduler = AsyncIOScheduler()
        self.start()

    def is_running(self) -> bool:
        """Check if scheduler is currently running."""
        return self.scheduler.running


# Singleton instance
scheduler_service = SchedulerService()
