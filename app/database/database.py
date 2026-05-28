"""
Database connection e configurazione per PostgreSQL.

Questo modulo gestisce:
- Connessione a PostgreSQL tramite DATABASE_URL
- Creazione delle tabelle (alembic migrations)
- Sessioni SQLAlchemy
- Helper per operazioni comuni su utenti
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from typing import Optional
import bcrypt

from ..config import settings
from .models import Base, User

# 🔗 Crea l'engine usando la DATABASE_URL da config
# La URL è nel formato: postgresql+psycopg://user:password@localhost/database
engine = create_engine(
    settings.database_url,
    echo=False,  # Cambia a True per debug (stampa le query SQL)
    poolclass=NullPool  # Ogni richiesta usa una nuova connessione
)

# SessionLocal: factory per creare nuove sessioni di database
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def init_db():
    """
    Inizializza il database creando tutte le tabelle.

    Questa funzione deve essere chiamata una sola volta all'avvio dell'applicazione.
    Se le tabelle esistono già, non fa nulla.

    Uso:
        from app.database.database import init_db
        init_db()  # Nel main.py dopo l'avvio dell'app
    """
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables initialized successfully!")


def get_db() -> Session:
    """
    Dependency injection per ottenere una sessione di database.

    Questa funzione è usata come dipendenza FastAPI negli endpoint.
    La sessione viene chiusa automaticamente dopo la richiesta.

    Uso in un endpoint:
        from fastapi import Depends
        from app.database.database import get_db

        @app.get("/users")
        async def get_users(db: Session = Depends(get_db)):
            users = db.query(User).all()
            return users

    Yields:
        Session: Sessione SQLAlchemy per operazioni sul database
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# Funzioni Helper per Operazioni Comuni su Utenti
# ============================================================================

def hash_password(password: str) -> str:
    """
    Hash di una password usando bcrypt.

    Bcrypt è uno degli algoritmi più sicuri per l'hashing delle password.
    Usa un salt casuale e un fattore di "cost" configurabile.

    Args:
        password (str): Password in chiaro da hashare

    Returns:
        str: Password hashata in formato bcrypt

    Esempio:
        hashed = hash_password("mypassword123")
        # hashed = b'$2b$12$...'
    """
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verifica una password confrontandola con il suo hash bcrypt.

    Args:
        password (str): Password in chiaro da verificare
        password_hash (str): Hash della password memorizzato nel database

    Returns:
        bool: True se la password è corretta, False altrimenti
    """
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


def create_user(db: Session, username: str, email: str, password: str, full_name: Optional[str] = None) -> User:
    """
    Crea un nuovo utente nel database.

    Args:
        db (Session): Sessione del database
        username (str): Username univoco (max 50 caratteri)
        email (str): Email univoca (max 100 caratteri)
        password (str): Password in chiaro (sarà hashata)
        full_name (Optional[str]): Nome completo opzionale

    Returns:
        User: L'utente appena creato
    """
    hashed_password = hash_password(password)

    db_user = User(
        username=username,
        email=email,
        password_hash=hashed_password,
        full_name=full_name,
        is_active=True
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Recupera un utente dal database per username."""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Recupera un utente dal database per email."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Recupera un utente dal database per ID."""
    return db.query(User).filter(User.id == user_id).first()


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    Autentica un utente verificando username e password.

    Questa è la funzione principale per il login.

    Args:
        db (Session): Sessione del database
        username (str): Username da verificare
        password (str): Password in chiaro da verificare

    Returns:
        Optional[User]: L'utente se le credenziali sono corrette, None altrimenti
    """
    user = get_user_by_username(db, username)

    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    if not user.is_active:
        return None

    return user


def list_all_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    """Elenca tutti gli utenti con paginazione."""
    return db.query(User).offset(skip).limit(limit).all()


def update_user(db: Session, user_id: int, **kwargs) -> Optional[User]:
    """Aggiorna i dati di un utente."""
    user = get_user_by_id(db, user_id)
    if not user:
        return None

    for key, value in kwargs.items():
        if hasattr(user, key) and key != 'password_hash':
            setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> bool:
    """Elimina un utente dal database."""
    user = get_user_by_id(db, user_id)
    if not user:
        return False

    db.delete(user)
    db.commit()
    return True
