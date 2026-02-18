from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import requests
import json

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("/ai/chat")
async def chat_with_ai(request: ChatRequest):
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: API Key is missing.")
        raise HTTPException(status_code=500, detail="API Key not configured")

    # print(f"DEBUG: Using API Key: {api_key[:5]}... (Length: {len(api_key)})")

    # OpenRouter Text Completion API (Direct HTTP)
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://skillnest-fullstack.vercel.app", 
        "X-Title": "SkillNest Chatbot"
    }
    
    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [{"role": "user", "content": request.message}]
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        if response.status_code != 200:
            print(f"AI API Error: {response.text}")
            raise HTTPException(status_code=response.status_code, detail=f"AI Provider Error: {response.text}")
            
        result = response.json()
        return {"reply": result["choices"][0]["message"]["content"]}
        
    except Exception as e:
        print(f"AI Internal Error: {e}")
        raise HTTPException(status_code=500, detail=f"AI Internal Error: {str(e)}")
