from fastapi import APIRouter, HTTPException, Depends, Response, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.schemas import UserCreate, UserLogin, UserResponse, TokenResponse
from api.auth.service import (
    get_user_by_username,
    create_new_user,
    authenticate,
    create_refresh_token,
)
from core.models import db_helper
from core.security import token_refresh

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
async def register(
    user_in: UserCreate,
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    user = await get_user_by_username(session=session, username=user_in.email)
    if user is not None:
        raise HTTPException(status_code=409, detail="User is already exist")
    return await create_new_user(session, user_in)


@router.post("/login", response_model=TokenResponse)
async def login(
    # user_in: UserLogin,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),  # в том числе
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    user_in = UserLogin(
        email=form_data.username, password=form_data.password
    )  # Для тестирования в OpenAPI
    token = await authenticate(session=session, user_in=user_in)
    refresh_token = await create_refresh_token(user_in=user_in, session=session)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=60 * 60 * 24 * 7,
        httponly=True,
        # secure=True,
        path="/auth/refresh",
    )
    return {"access_token": token, "token_type": "bearer"}


@router.post("/refresh")
async def refresh(refresh_token: str | None = Cookie(default=None)):
    token = token_refresh(refresh_token=refresh_token)
    return {"access_token": token, "token_type": "bearer"}


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        samesite="lax",
    )
    return {"detail": "Logged out"}
