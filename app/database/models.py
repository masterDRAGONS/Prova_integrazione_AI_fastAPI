"""
Database models per l'autenticazione e gestione utenti.

Questo modulo definisce i modelli SQLAlchemy per la persistenza dei dati
degli utenti nel database PostgreSQL.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base

# Base per tutti i modelli SQLAlchemy
Base = declarative_base()


class User(Base):
    """
    Modello per la tabella degli utenti.

    Attributi:
        id (int): Identificatore univoco dell'utente (primary key)
        username (str): Nome utente univoco, max 50 caratteri
        email (str): Email univoca dell'utente, max 100 caratteri
        password_hash (str): Hash della password (bcrypt), max 255 caratteri
        full_name (str): Nome completo dell'utente, opzionale, max 100 caratteri
        is_active (bool): Flag per abilitare/disabilitare l'account (default: True)
        created_at (datetime): Timestamp di creazione dell'utente (UTC)
        updated_at (datetime): Timestamp dell'ultimo aggiornamento (UTC)
    """

    __tablename__ = "users"

    # Colonna ID primaria
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Username univoco e indicizzato per ricerche veloci
    username = Column(String(50), unique=True, index=True, nullable=False)

    # Email univoca e indicizzata
    email = Column(String(100), unique=True, index=True, nullable=False)

    # Hash della password (NON la password in chiaro!)
    password_hash = Column(String(255), nullable=False)

    # Nome completo opzionale
    full_name = Column(String(100), nullable=True)

    # Flag per account attivi/disattivati
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamp di creazione (impostato al momento della creazione)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Timestamp di ultimo aggiornamento (aggiornato ad ogni modifica)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        """Rappresentazione stringa dell'utente per debugging."""
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
