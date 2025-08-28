from typing import Generator
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.token import TokenPayload
from app.crud.crud_user import user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme), request: Request = None
) -> User:
    from app.core.security import create_access_token, decode_token
    from datetime import timedelta
    refresh_token = None
    if request:
        refresh_token = request.headers.get("X-Refresh-Token")
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=["HS256"]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError) as e:
        # If token is expired and refresh token is provided, try to refresh
        if refresh_token:
            try:
                payload = decode_token(refresh_token)
                if payload.get("type") != "refresh":
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
                user_id = payload.get("sub")
                if not user_id:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
                # Issue new access token (optionally, you could return it in a header or response)
                access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
                new_access_token = create_access_token(user_id, expires_delta=access_token_expires)
                # Optionally, attach new_access_token to request.state or response
                user_obj = user.get(db, id=user_id)
                if not user_obj:
                    raise HTTPException(status_code=404, detail="User not found")
                return user_obj
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Could not validate credentials (refresh failed)",
                )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user_obj = user.get(db, id=token_data.sub)
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")
    return user_obj

def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
