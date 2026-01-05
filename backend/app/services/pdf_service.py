"""PDF download and management service."""

import logging
import os
from pathlib import Path
from typing import Optional
from datetime import datetime

import aiohttp

from app.config import settings

logger = logging.getLogger(__name__)


class PDFService:
    """Service for downloading and managing PDF files."""

    def __init__(self):
        """Initialize PDF service."""
        self.papers_dir = settings.PAPERS_DIR

    def _get_category_path(self, category: str, date: Optional[datetime] = None) -> Path:
        """
        Get the directory path for a category and date.
        """
        date_str = (date or datetime.now()).strftime("%Y-%m-%d")
        return self.papers_dir / category / date_str

    def _get_pdf_path(self, arxiv_id: str, category: str, date: Optional[datetime] = None) -> Path:
        """
        Get the full path for a PDF file.
        """
        category_path = self._get_category_path(category, date)
        return category_path / f"{arxiv_id}.pdf"

    async def download_pdf(
        self,
        arxiv_id: str,
        pdf_url: str,
        category: str,
        date: Optional[datetime] = None,
    ) -> Optional[str]:
        """
        Download a PDF file from ArXiv.
        """
        pdf_path = self._get_pdf_path(arxiv_id, category, date)

        # Check if already exists
        if pdf_path.exists():
            logger.info(f"PDF already exists: {pdf_path}")
            return str(pdf_path)

        # Create directory structure
        pdf_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            logger.info(f"Downloading PDF: {arxiv_id} from {pdf_url}")

            async with aiohttp.ClientSession() as session:
                async with session.get(pdf_url, timeout=aiohttp.ClientTimeout(total=60)) as response:
                    response.raise_for_status()
                    content = await response.read()

            # Save file
            with open(pdf_path, "wb") as f:
                f.write(content)

            logger.info(f"Successfully downloaded: {pdf_path}")
            return str(pdf_path)

        except Exception as e:
            logger.error(f"Failed to download PDF {arxiv_id}: {e}")
            # Clean up partial download
            if pdf_path.exists():
                pdf_path.unlink()
            return None

    def get_pdf_path(self, arxiv_id: str, category: str, date: Optional[datetime] = None) -> Optional[str]:
        """Get the path to an existing PDF file."""
        pdf_path = self._get_pdf_path(arxiv_id, category, date)
        if pdf_path.exists():
            return str(pdf_path)
        return None

    def delete_pdf(self, arxiv_id: str, category: str, date: Optional[datetime] = None) -> bool:
        """Delete a PDF file."""
        pdf_path = self._get_pdf_path(arxiv_id, category, date)
        if pdf_path.exists():
            pdf_path.unlink()
            logger.info(f"Deleted PDF: {pdf_path}")
            return True
        return False

    def pdf_exists(self, arxiv_id: str, category: str, date: Optional[datetime] = None) -> bool:
        """Check if a PDF file exists."""
        return self._get_pdf_path(arxiv_id, category, date).exists()


# Singleton instance
pdf_service = PDFService()
