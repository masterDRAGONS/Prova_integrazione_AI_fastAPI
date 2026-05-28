from fastapi import FastAPI, Form
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from .config import settings
from .ai.gemini import Gemini
from .schemas import ChatRequest, ChatResponse
from pathlib import Path

app = FastAPI()

# Configurazione template Jinja2
templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


def load_system_prompt():
    try:
        with open("app/prompts/system_prompt.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return None


system_prompt = load_system_prompt()
ai_platform = Gemini(api_key=settings.gemini_api_key, system_prompt=system_prompt)


# --- Web Endpoints (HTML) ---
@app.get("/", response_class=str)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/", response_class=str)
async def chat_form(request: Request, prompt: str = Form(...)):
    response_text = ai_platform.chat(prompt)
    return templates.TemplateResponse(
        "chat.html",
        {"request": request, "prompt": prompt, "response": response_text}
    )


# --- API Endpoints (JSON) ---
@app.post("/api/chat", response_model=ChatResponse)
async def chat_api(request: ChatRequest):
    response_text = ai_platform.chat(request.prompt)
    return ChatResponse(response=response_text)