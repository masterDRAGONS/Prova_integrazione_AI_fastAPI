"""
User management endpoints for registration and user creation.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import re

from ..config import settings
from ..database import (
    get_db,
    create_user,
    get_user_by_username,
    get_user_by_email
)

router = APIRouter(prefix="/api/users", tags=["users"])


class UserRegisterRequest(BaseModel):
    """Schema per la registrazione di un nuovo utente."""
    username: str = Field(..., min_length=3, max_length=50, description="Username univoco")
    email: str = Field(..., description="Email valida e univoca")
    password: str = Field(..., min_length=8, description="Password di almeno 8 caratteri")
    full_name: str = Field(None, max_length=100, description="Nome completo (opzionale)")

    def validate_email(self) -> bool:
        """Valida il formato dell'email."""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, self.email) is not None


class UserResponse(BaseModel):
    """Schema per la risposta con i dati dell'utente."""
    id: int
    username: str
    email: str
    full_name: str = None
    is_active: bool

    class Config:
        from_attributes = True


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegisterRequest, db: Session = Depends(get_db)):
    """
    Registra un nuovo utente nel database.

    - **username**: Deve essere univoco, tra 3 e 50 caratteri
    - **email**: Deve essere valida e univoca
    - **password**: Almeno 8 caratteri (viene hashata con bcrypt)
    - **full_name**: Opzionale, massimo 100 caratteri
    """

    # Valida il formato dell'email
    if not user_data.validate_email():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email non valida"
        )

    # Controlla se username è già in uso
    existing_user = get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username '{user_data.username}' è già in uso"
        )

    # Controlla se email è già in uso
    existing_email = get_user_by_email(db, user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{user_data.email}' è già registrata"
        )

    # Crea il nuovo utente
    try:
        new_user = create_user(
            db=db,
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name
        )
        return new_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Errore durante la creazione dell'utente"
        )
