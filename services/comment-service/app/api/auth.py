import httpx
from typing import Optional
from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.comment_service import CommentService


async def get_current_user(authorization: str = Header(..., alias="Authorization")) -> dict:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = authorization[7:]  # Remove "Bearer " prefix

    # Verify token with user service
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://user-service:8002/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Authentication service unavailable")


async def get_current_user_optional(authorization: Optional[str] = Header(None, alias="Authorization")) -> Optional[dict]:
    if not authorization or not authorization.startswith("Bearer "):
        return None

    token = authorization[7:]

    # Verify token with user service
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://user-service:8002/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200:
                return response.json()
    except Exception:
        pass
    return None