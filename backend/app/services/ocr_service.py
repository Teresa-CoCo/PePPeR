"""OCR service using PaddleOCR and PyMuPDF fallback."""

import base64
import logging
from pathlib import Path
from typing import Optional

import fitz  # PyMuPDF
import requests

from app.config import settings

logger = logging.getLogger(__name__)


class OCRService:
    """Service for extracting text from PDFs using PaddleOCR or PyMuPDF."""

    def __init__(self):
        """Initialize OCR service."""
        self.api_url = settings.PADDLEOCR_API_URL
        self.token = settings.PADDLEOCR_TOKEN

    def _encode_pdf(self, pdf_path: str) -> str:
        """Encode PDF file as base64."""
        with open(pdf_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def _call_paddleocr(self, pdf_path: str) -> Optional[str]:
        """
        Call PaddleOCR API to extract text from PDF.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Extracted text or None if failed
        """
        if not self.token:
            logger.warning("PaddleOCR token not configured")
            return None

        try:
            # Encode PDF as base64
            pdf_base64 = self._encode_pdf(pdf_path)

            # Prepare request payload
            payload = {
                "image": pdf_base64,
                "recognize_long": True,
                "rotate": True,
            }

            headers = {"Content-Type": "application/json"}

            # Add access token to URL
            url = f"{self.api_url}?access_token={self.token}"

            response = requests.post(url, json=payload, headers=headers, timeout=120)
            response.raise_for_status()

            result = response.json()

            # Parse PaddleOCR response
            if result.get("success"):
                texts = []
                for item in result.get("results", []):
                    rec_texts = item.get("rec_texts", [])
                    texts.extend(rec_texts)
                return "\n".join(texts)

            return None

        except requests.RequestException as e:
            logger.error(f"PaddleOCR API error: {e}")
            return None
        except Exception as e:
            logger.error(f"PaddleOCR processing error: {e}")
            return None

    def _extract_with_pymupdf(self, pdf_path: str) -> Optional[str]:
        """
        Extract text from PDF using PyMuPDF as fallback.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Extracted text or None if failed
        """
        try:
            doc = fitz.open(pdf_path)
            text_parts = []

            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                if text.strip():
                    text_parts.append(text)

            doc.close()
            extracted = "\n".join(text_parts)
            logger.info(f"Extracted {len(extracted)} characters with PyMuPDF")
            return extracted

        except Exception as e:
            logger.error(f"PyMuPDF extraction error: {e}")
            return None

    def extract_text(self, pdf_path: str) -> Optional[str]:
        """
        Extract text from a PDF file.

        First tries PaddleOCR API, then falls back to PyMuPDF.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Extracted text or None if extraction failed
        """
        pdf = Path(pdf_path)
        if not pdf.exists():
            logger.error(f"PDF file not found: {pdf_path}")
            return None

        # Try PaddleOCR first
        if self.token:
            logger.info(f"Attempting PaddleOCR extraction for {pdf_path}")
            text = self._call_paddleocr(pdf_path)
            if text:
                logger.info(f"PaddleOCR extracted {len(text)} characters")
                return text

        # Fallback to PyMuPDF
        logger.info(f"Falling back to PyMuPDF for {pdf_path}")
        return self._extract_with_pymupdf(pdf_path)


# Singleton instance
ocr_service = OCRService()
