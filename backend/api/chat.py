from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from openai import OpenAI

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("/ai/chat")
async def chat_with_ai(request: ChatRequest):
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="API Key not configured")

    # If using OpenRouter, we need to set the base url
    base_url = "https://openrouter.ai/api/v1" if "OPENROUTER" in os.environ.keys() or os.getenv("OPENROUTER_API_KEY") else None
    
    # User provided code uses 'gpt-4o-mini', assuming OpenAI standard or OpenRouter mapping
    # Adjusting to be robust
    client = OpenAI(
        api_key=api_key,
        base_url=base_url
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", # Or "openai/gpt-3.5-turbo" if using OpenRouter specific
            messages=[{"role": "user", "content": request.message}]
        )
        return {"reply": response.choices[0].message.content}
    except Exception as e:
        print(f"AI Error: {e}")
        # Fallback for demo purposes if quota is full etc, but better to return error
        raise HTTPException(status_code=500, detail=str(e))
