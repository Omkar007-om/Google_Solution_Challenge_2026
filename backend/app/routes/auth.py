"""
SAR Multi-Agent Backend — Auth Routes
====================================
JWT-based demo authentication for the SAR UI.
Replace with a real IdP (OIDC) in production.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.config import get_settings
from app.core.security import create_access_token, get_current_user

router = APIRouter(tags=["Auth"])


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=128)
    password: str = Field(..., min_length=1, max_length=256)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class MeResponse(BaseModel):
    username: str
    claims: dict


@router.post(
    "/auth/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Login (JWT)",
    description="Returns a short-lived JWT access token for API calls.",
)
async def login(body: LoginRequest) -> TokenResponse:
    settings = get_settings()
    if body.username != settings.auth_demo_username or body.password != settings.auth_demo_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"success": False, "error": "Invalid credentials"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    token, expires_in = create_access_token(sub=body.username, claims={"role": "analyst"})
    return TokenResponse(access_token=token, expires_in=expires_in)


@router.get(
    "/auth/me",
    response_model=MeResponse,
    status_code=status.HTTP_200_OK,
    summary="Current user",
)
async def me(user=Depends(get_current_user)) -> MeResponse:
    return MeResponse(username=user["username"], claims=user["claims"])

