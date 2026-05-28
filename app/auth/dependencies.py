from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from ..config import settings

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
