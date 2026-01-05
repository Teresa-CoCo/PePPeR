"""LLM service using OpenRouter API."""

import json
import logging
from typing import AsyncGenerator, Dict, List, Optional

from openai import AsyncOpenAI

from app.config import settings
from app.models.paper import AIAnalysis

logger = logging.getLogger(__name__)


class LLMService:
    """Service for LLM interactions via OpenRouter."""

    def __init__(self):
        """Initialize LLM service."""
        self.client = AsyncOpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
        )
        self.default_model = settings.OPENROUTER_DEFAULT_MODEL

    async def explain_abstract(self, abstract: str) -> str:
        """
        Generate a clear explanation of an abstract.

        Args:
            abstract: The paper abstract to explain

        Returns:
            Clear explanation of the abstract
        """
        if not abstract:
            return ""

        response = await self.client.chat.completions.create(
            model=self.default_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a research assistant. Explain this academic abstract "
                        "clearly and concisely for a researcher. Focus on the key "
                        "contribution and methodology. Keep it brief (2-3 sentences)."
                    ),
                },
                {"role": "user", "content": abstract},
            ],
            temperature=0.3,
            max_tokens=200,
        )

        return response.choices[0].message.content or ""

    async def analyze_paper(
        self,
        title: str,
        abstract: str,
        full_text: Optional[str] = None,
    ) -> AIAnalysis:
        """
        Generate comprehensive analysis of a paper.

        Args:
            title: Paper title
            abstract: Paper abstract
            full_text: Optional full text for deeper analysis

        Returns:
            AIAnalysis with summary, key findings, etc.
        """
        context = f"Title: {title}\n\nAbstract: {abstract}"
        if full_text:
            # Truncate full text to fit context window
            context = f"{context}\n\nFull Text (excerpt):\n{full_text[:15000]}"

        response = await self.client.chat.completions.create(
            model=self.default_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a research assistant analyzing an academic paper. "
                        "Provide a structured analysis with: 1. A concise summary (2-3 sentences) "
                        "2. Key findings (bullet points) 3. Methodology overview 4. Strengths "
                        "5. Limitations 6. Relevance score (0-100) for ML/AI research. "
                        "Return as JSON with keys: summary, key_findings (list), methodology, "
                        "strengths (list), limitations (list), relevance_score."
                    ),
                },
                {"role": "user", "content": context},
            ],
            temperature=0.3,
            max_tokens=1000,
        )

        content = response.choices[0].message.content or "{}"

        # Parse JSON response
        try:
            # Handle potential markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            data = json.loads(content)
            return AIAnalysis(
                summary=data.get("summary", ""),
                key_findings=data.get("key_findings", []),
                methodology=data.get("methodology"),
                strengths=data.get("strengths", []),
                limitations=data.get("limitations", []),
                relevance_score=data.get("relevance_score"),
            )
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse LLM analysis: {e}")
            return AIAnalysis(summary=content[:500])

    async def chat_with_context(
        self,
        paper_text: str,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat responses with paper context.

        Args:
            paper_text: Full text of the paper
            messages: Chat history with latest user message
            model: Optional model override

        Returns:
            Async generator yielding streaming response chunks
        """
        selected_model = model or self.default_model

        # Build context with system prompt
        truncated_text = paper_text[:50000]
        system_prompt = (
            "You are a research assistant helping a user understand an academic paper. "
            "You must answer based ONLY on the provided paper content. "
            "If the answer cannot be found in the paper, say so clearly. "
            f"Paper content:\n{truncated_text}\n\nCurrent conversation:"
        )

        # Construct full message list
        full_messages = [{"role": "system", "content": system_prompt}] + messages

        try:
            stream = await self.client.chat.completions.create(
                model=selected_model,
                messages=full_messages,
                temperature=0.3,
                max_tokens=4000,
                stream=True,
            )

            async for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield content

        except Exception as e:
            logger.error(f"LLM streaming error: {e}")
            yield f"Error: {str(e)}"


# Singleton instance
llm_service = LLMService()
