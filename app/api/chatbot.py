from fastapi import APIRouter, Depends, HTTPException
import httpx

from app.db import models, schemas
from app.core.security import get_current_user

router = APIRouter(prefix="/api/chatbot", tags=["Chatbot"])

# This would be the URL of your external RAG/Gemini service
GEMINI_SERVICE_URL = "https://your.external.ai.service/api/ask"

@router.post("/ask", response_model=schemas.ChatbotResponse)
async def ask_chatbot(
    query: schemas.ChatbotQuery,
    current_user: models.User = Depends(get_current_user),
):
    """
    Acts as a secure gateway to an external chatbot/RAG service.
    """
    print(f"User {current_user.email} is asking: '{query.question}'")

    try:
        # --- Placeholder Logic ---
        # In a real scenario, you'd make a call to your AI service.
        # async with httpx.AsyncClient() as client:
        #     response = await client.post(GEMINI_SERVICE_URL, json=query.dict())
        #     response.raise_for_status()
        #     answer = response.json().get("answer")

        # For demonstration, we'll echo a formatted response.
        answer = f"As an AI, I've processed your question about '{query.question}' for the Nashik region. Here is your detailed guidance..."
        # --- End Placeholder ---

        if not answer:
            raise HTTPException(status_code=500, detail="Failed to get a response from the AI service.")

        return schemas.ChatbotResponse(answer=answer)

    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"AI service is unavailable: {exc}")