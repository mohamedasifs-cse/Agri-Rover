"""POST /api/chat — AI assistant chat endpoint."""

import asyncio
from fastapi import APIRouter
from models.schemas import ChatRequest, ChatResponse
from services.chat_service import generate_response

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a farmer's question and return an AI-generated response.

    Phase 1: Rule-based response engine.
    Phase 3: Replace generate_response() with Claude API or LLaMA inference.
    """
    # Simulate realistic response latency (600ms)
    await asyncio.sleep(0.6)

    response_text, context_used = generate_response(request.message)
    return ChatResponse(response=response_text, context_used=context_used)


@router.get("/suggestions")
async def get_suggestions():
    """Return suggested questions for the chat UI."""
    return {
        "suggestions": [
            "What disease was found?",
            "How serious is it?",
            "Where is the affected area?",
            "What should I do now?",
            "How is the weather today?",
            "How to prevent this disease?",
            "Show me the detection history",
            "How many healthy plants do I have?",
        ]
    }
