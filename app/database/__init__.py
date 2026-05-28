"""
Package database per la gestione della persistenza dei dati.

Moduli:
    models: Definizione dei modelli SQLAlchemy (ORM)
    database: Configurazione PostgreSQL e funzioni helper
"""

from .models import User, Base
from .database import (
    init_db,
    get_db,
    hash_password,
    verify_password,
    create_user,
    get_user_by_username,
    get_user_by_email,
    get_user_by_id,
    authenticate_user,
    list_all_users,
    update_user,
    delete_user,
)

__all__ = [
    "User",
    "Base",
    "init_db",
    "get_db",
    "hash_password",
    "verify_password",
    "create_user",
    "get_user_by_username",
    "get_user_by_email",
    "get_user_by_id",
    "authenticate_user",
    "list_all_users",
    "update_user",
    "delete_user",
]
