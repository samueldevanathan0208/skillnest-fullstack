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
        print("ERROR: API Key is missing.")
        raise HTTPException(status_code=500, detail="API Key not configured")

    print(f"DEBUG: Using API Key: {api_key[:5]}... (Length: {len(api_key)})")

    # OpenRouter Configuration
    base_url = "https://openrouter.ai/api/v1"
    
    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
        default_headers={
            "HTTP-Referer": "http://localhost:3000", # Required by OpenRouter for ranking
            "X-Title": "SkillNest Chatbot"
        }
    )

    try:
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini", # Explicit OpenRouter model ID
            messages=[{"role": "user", "content": request.message}]
        )
        return {"reply": response.choices[0].message.content}
    except Exception as e:
        print(f"AI Error: {e}")
        raise HTTPException(status_code=500, detail=f"AI Error: {str(e)}")
