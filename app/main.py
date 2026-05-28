from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, status, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from jose import jwt
from sqlalchemy.orm import Session
from starlette.requests import Request

from .ai.gemini import Gemini
from .auth.dependencies import get_user_identifier
from .auth.throttling import apply_rate_limit
from .config import settings
from .schemas import ChatRequest, ChatResponse
from .routers import users_router
from .database import get_db, authenticate_user

app = FastAPI()

# Include routers
app.include_router(users_router)

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


# --- Authentication Helpers ---
def create_access_token(username: str, expires_delta: timedelta = None):
    to_encode = {"sub": username}
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


# --- Web Endpoints (HTML) ---
@app.get("/")
async def index(request: Request):
    token = request.cookies.get("token")
    user_id = await get_user_identifier(token)

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "request": request,
            "user_id": user_id,
            "token": token,
            "rate_limit": settings.auth_rate_limit if user_id != "global_unauthenticated_user" else settings.global_rate_limit,
            "max_rate_limit": settings.auth_rate_limit if user_id != "global_unauthenticated_user" else settings.global_rate_limit,
        }
    )


@app.post("/")
async def chat_form(request: Request, prompt: str = Form(...)):
    token = request.cookies.get("token")
    user_id = await get_user_identifier(token)

    # Apply rate limiting
    apply_rate_limit(user_id)

    response_text = ai_platform.chat(prompt)
    return templates.TemplateResponse(
        request,
        "chat.html",
        {
            "request": request,
            "user_id": user_id,
            "prompt": prompt,
            "response": response_text
        }
    )


@app.get("/login")
async def login_page(request: Request, error: str = None):
    return templates.TemplateResponse(
        request,
        "login.html",
        {"request": request, "error": error}
    )


@app.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse(
        request,
        "register.html",
        {"request": request}
    )


@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    # Authenticate user against database
    user = authenticate_user(db, username, password)
    if not user:
        return templates.TemplateResponse(
            request,
            "login.html",
            {"request": request, "error": "Username o password non validi"},
            status_code=401
        )

    # Create JWT token
    access_token = create_access_token(username)

    # Redirect to home with token in cookie
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="token", value=access_token, httponly=True)
    return response


@app.post("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="token")
    return response


@app.get("/token")
async def get_token(username: str, password: str, db: Session = Depends(get_db)):
    user = authenticate_user(db, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    access_token = create_access_token(username)
    return {"access_token": access_token, "token_type": "bearer"}


# --- API Endpoints (JSON) ---
@app.post("/api/chat", response_model=ChatResponse)
async def chat_api(request: ChatRequest):
    response_text = ai_platform.chat(request.prompt)
    return ChatResponse(response=response_text)