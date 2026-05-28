from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db, get_user_by_username, User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


async def get_user_identifier(token: Optional[str] = Depends(oauth2_scheme)):
    """
    Extracts user identifier from JWT token or returns global user identifier.

    Args:
        token: Optional JWT token from Authorization header

    Returns:
        str: Username from token or "global_unauthenticated_user" if no token

    Raises:
        HTTPException: If token is invalid or malformed
    """
    if token is None:
        return "global_unauthenticated_user"

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    return username


async def get_authenticated_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency per proteggere endpoint che richiedono autenticazione.
    Solleva 401 se l'utente non è autenticato.

    Args:
        token: JWT token dal header Authorization o cookie
        db: Sessione del database

    Returns:
        User: L'utente autenticato dal database

    Raises:
        HTTPException: Se il token è invalido, scaduto, o l'utente non esiste
    """

    # Se non c'è token, utente non autenticato
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verifica il token e ottiene l'username
    username = await get_user_identifier(token)

    # Se è l'utente anonimo, non è autenticato
    if username == "global_unauthenticated_user":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Cerca l'utente nel database
    user = get_user_by_username(db, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
