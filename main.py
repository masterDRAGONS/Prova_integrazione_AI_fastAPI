import os
from fastapi import FastAPI
from .ai.gemini import Gemini


from .schemas import (
    ChatRequest,    ChatResponse,
)
# --- App Initialization ---
app = FastAPI()








# --- AI Configuration ---
def load_system_prompt():
    try:
        with open("src/prompts/system_prompt.md", "r") as f:
            return f.read()
    except FileNotFoundError:
        return None


system_prompt = load_system_prompt()
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set.")

ai_platform = Gemini(api_key=gemini_api_key, system_prompt=system_prompt)


# --- API Endpoints ---
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # TODO: implement ai integration
    response_text = ""
    return ChatResponse(response=response_text)


@app.get("/")
async def root():
    return {"message": "API is running"}