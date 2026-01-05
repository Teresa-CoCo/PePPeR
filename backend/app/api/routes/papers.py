"""Papers API routes."""

import os
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import FileResponse

from app.services.arxiv_service import arxiv_client
from app.services.pdf_service import pdf_service
from app.services.ocr_service import ocr_service
from app.services.llm_service import llm_service
from app.services.data_store import data_store
from app.models.paper import Paper, PaperMetadata, AIAnalysis
from app.models.schemas import (
    PaperResponse,
    PaperDetailResponse,
    FetchRequest,
    FetchResponse,
    ProcessRequest,
    ProcessResponse,
    ListPapersRequest,
)

router = APIRouter()


@router.get("")
async def list_papers(
    category: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    processed: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> list[PaperResponse]:
    """List papers with optional filters."""
    papers = data_store.list_papers(
        category=category,
        date_from=date_from,
        date_to=date_to,
        processed=processed,
        search=search,
        limit=limit,
        offset=offset,
    )

    return [
        PaperResponse(
            arxiv_id=p.metadata.arxiv_id,
            title=p.metadata.title,
            authors=[a.name for a in p.metadata.authors],
            abstract=p.metadata.abstract,
            published_date=p.metadata.published_date,
            category=p.metadata.primary_category,
            ai_summary=p.ai_analysis.summary if p.ai_analysis else None,
            processed=p.processed,
        )
        for p in papers
    ]


@router.get("/categories")
async def get_categories() -> list[dict]:
    """Get list of available arXiv categories."""
    return [
        {"id": "cs.AI", "name": "Artificial Intelligence"},
        {"id": "cs.CL", "name": "Computation and Language"},
        {"id": "cs.CV", "name": "Computer Vision"},
        {"id": "cs.LG", "name": "Machine Learning"},
        {"id": "cs.NE", "name": "Neural and Evolutionary Computing"},
        {"id": "cs.RO", "name": "Robotics"},
        {"id": "cs.SE", "name": "Software Engineering"},
        {"id": "cs.CR", "name": "Cryptography and Security"},
        {"id": "cs.DB", "name": "Databases"},
        {"id": "cs.DC", "name": "Distributed Computing"},
        {"id": "cs.HC", "name": "Human-Computer Interaction"},
        {"id": "cs.IR", "name": "Information Retrieval"},
        {"id": "stat.ML", "name": "Statistics - Machine Learning"},
    ]


@router.post("/fetch")
async def fetch_papers(request: FetchRequest) -> FetchResponse:
    """Fetch papers from arXiv for a category."""
    # Parse date
    fetch_date = None
    if request.date:
        try:
            fetch_date = datetime.strptime(request.date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    # Fetch from arXiv
    try:
        papers_data = arxiv_client.fetch_by_category(request.category, fetch_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch from arXiv: {str(e)}")

    papers_downloaded = 0
    saved_papers = []

    for metadata in papers_data:
        # Create paper entry
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

        # Save to data store
        if data_store.add_paper(paper):
            saved_papers.append(paper)

    return FetchResponse(
        category=request.category,
        date=request.date or datetime.now().strftime("%Y-%m-%d"),
        papers_found=len(papers_data),
        papers_downloaded=papers_downloaded,
        papers=[
            PaperResponse(
                arxiv_id=p.metadata.arxiv_id,
                title=p.metadata.title,
                authors=[a.name for a in p.metadata.authors],
                abstract=p.metadata.abstract,
                published_date=p.metadata.published_date,
                category=p.metadata.primary_category,
                processed=p.processed,
            )
            for p in saved_papers
        ],
    )


@router.get("/{arxiv_id}")
async def get_paper(arxiv_id: str) -> PaperDetailResponse:
    """Get detailed paper information."""
    paper = data_store.get_paper(arxiv_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    return PaperDetailResponse(
        metadata=paper.metadata,
        pdf_path=paper.pdf_path,
        extracted_text=paper.extracted_text,
        ai_analysis=paper.ai_analysis,
        chat_history=paper.chat_history,
        processed=paper.processed,
    )


@router.get("/{arxiv_id}/pdf")
async def get_paper_pdf(arxiv_id: str):
    """Serve the PDF file for a paper."""
    paper = data_store.get_paper(arxiv_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    if not paper.pdf_path or not os.path.exists(paper.pdf_path):
        raise HTTPException(status_code=404, detail="PDF file not found")

    return FileResponse(
        paper.pdf_path,
        media_type="application/pdf",
        filename=f"{arxiv_id}.pdf",
    )


@router.post("/{arxiv_id}/process")
async def process_paper(arxiv_id: str, request: ProcessRequest) -> ProcessResponse:
    """Process a paper: OCR extraction and AI analysis."""
    paper = data_store.get_paper(arxiv_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    if not paper.pdf_path or not os.path.exists(paper.pdf_path):
        raise HTTPException(status_code=400, detail="PDF file not found")

    ocr_success = False
    text_extracted = False
    ai_analysis_generated = False

    # OCR extraction
    if not request.skip_ocr:
        try:
            text = ocr_service.extract_text(paper.pdf_path)
            if text:
                data_store.set_extracted_text(arxiv_id, text)
                text_extracted = True
                ocr_success = True
        except Exception as e:
            # Fallback to PyMuPDF
            try:
                text = ocr_service._extract_with_pymupdf(paper.pdf_path)
                if text:
                    data_store.set_extracted_text(arxiv_id, text)
                    text_extracted = True
                    ocr_success = True
            except Exception:
                pass

    # AI analysis
    try:
        # Use abstract first, then full text if available
        context = paper.metadata.abstract
        if paper.extracted_text:
            context = paper.extracted_text

        analysis = llm_service.analyze_paper(
            title=paper.metadata.title,
            abstract=paper.metadata.abstract,
            full_text=paper.extracted_text,
        )

        if analysis:
            data_store.set_ai_analysis(arxiv_id, analysis)
            ai_analysis_generated = True
    except Exception as e:
        pass

    # Mark as processed
    data_store.set_processed(arxiv_id, True)

    return ProcessResponse(
        arxiv_id=arxiv_id,
        ocr_success=ocr_success,
        text_extracted=text_extracted,
        ai_analysis_generated=ai_analysis_generated,
        message="Processing complete" if ai_analysis_generated else "Partial processing completed",
    )


@router.get("/{arxiv_id}/explain")
async def explain_paper(arxiv_id: str) -> dict:
    """Get AI explanation for a paper's abstract."""
    paper = data_store.get_paper(arxiv_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    try:
        explanation = llm_service.explain_abstract(paper.metadata.abstract)
        return {"explanation": explanation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate explanation: {str(e)}")
