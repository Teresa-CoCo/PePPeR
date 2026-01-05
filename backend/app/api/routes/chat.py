"""Chat API routes for paper Q&A."""

import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException

from app.models.paper import ChatMessage
from app.models.schemas import ChatRequest, ChatResponse
from app.services.data_store import data_store
from app.services.llm_service import llm_service
from sse_starlette.sse import EventSourceResponse

router = APIRouter()


async def chat_event_generator(arxiv_id: str, user_message: str, model: Optional[str] = None):
    """Generate SSE events for streaming chat response."""
    paper = data_store.get_paper(arxiv_id)
    if not paper:
        yield {"event": "error", "data": "Paper not found"}
        return

    if not paper.extracted_text:
        yield {"event": "error", "data": "Paper text not extracted. Please process the paper first."}
        return

    # Build messages list from chat history
    messages = [
        {"role": msg.role, "content": msg.content}
        for msg in paper.chat_history[-10:]  # Last 10 messages for context
    ]
    messages.append({"role": "user", "content": user_message})

    # Add user message to history
    user_msg = ChatMessage(role="user", content=user_message, timestamp=datetime.utcnow())
    data_store.add_chat_message(arxiv_id, user_msg)

    # Stream response
    response_text = ""
    async for chunk in llm_service.chat_with_context(
        paper_text=paper.extracted_text,
        messages=messages,
        model=model,
    ):
        response_text += chunk
        yield {"event": "message", "data": chunk}

    # Add assistant message to history
    assistant_msg = ChatMessage(
        role="assistant",
        content=response_text,
        timestamp=datetime.utcnow()
    )
    data_store.add_chat_message(arxiv_id, assistant_msg)

    yield {"event": "done", "data": ""}


@router.post("/{arxiv_id}")
async def chat_with_paper(arxiv_id: str, request: ChatRequest):
    """
    Stream chat response for a paper.

    Uses Server-Sent Events (SSE) for streaming.
    """
    paper = data_store.get_paper(arxiv_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    if not paper.extracted_text:
        raise HTTPException(
            status_code=400,
            detail="Paper text not extracted. Please process the paper first."
        )

    return EventSourceResponse(
        chat_event_generator(arxiv_id, request.message, request.model)
    )


@router.get("/{arxiv_id}/history")
async def get_chat_history(arxiv_id: str):
    """Get chat history for a paper."""
    paper = data_store.get_paper(arxiv_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    return [
        {"role": msg.role, "content": msg.content, "timestamp": msg.timestamp.isoformat()}
        for msg in paper.chat_history
    ]


@router.delete("/{arxiv_id}")
async def clear_chat_history(arxiv_id: str):
    """Clear chat history for a paper."""
    if not data_store.get_paper(arxiv_id):
        raise HTTPException(status_code=404, detail="Paper not found")

    data_store.clear_chat_history(arxiv_id)
    return {"message": "Chat history cleared"}


@router.post("/{arxiv_id}/generate-summary")
async def generate_paper_summary(arxiv_id: str):
    """
    Generate a comprehensive summary of the paper.

    Uses the full extracted text to create a detailed understanding.
    """
    paper = data_store.get_paper(arxiv_id)
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    if not paper.extracted_text:
        raise HTTPException(
            status_code=400,
            detail="Paper text not extracted. Please process the paper first."
        )

    # Generate comprehensive analysis
    analysis = await llm_service.analyze_paper(
        title=paper.metadata.title,
        abstract=paper.metadata.abstract,
        full_text=paper.extracted_text,
    )

    # Save analysis
    data_store.set_ai_analysis(arxiv_id, analysis)

    return {
        "summary": analysis.summary,
        "key_findings": analysis.key_findings,
        "methodology": analysis.methodology,
        "strengths": analysis.strengths,
        "limitations": analysis.limitations,
    }
