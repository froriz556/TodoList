from fastapi import APIRouter, HTTPException, Depends, Response, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
    VerifyEmail,
    VerifyPassword,
)
from api.auth.service import (
    get_user_by_username,
    create_new_user,
    authenticate,
    create_refresh_token,
    create_confirm_code,
    verify_confirm_codes_and_update_user,
)
from core.models import db_helper
from core.models.redis_helper import (
    VerificationCodesCache,
    get_confirm_codes_cache,
    ResetCodesCache,
    get_reset_codes_cache,
)
from core.models.users import User
from core.security import token_refresh, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
async def register(
    user_in: UserCreate,
    session: AsyncSession = Depends(db_helper.session_dependency),
    cache: VerificationCodesCache = Depends(get_confirm_codes_cache),
):
    user = await get_user_by_username(session=session, username=user_in.email)
    if user is not None:
        raise HTTPException(status_code=409, detail="User is already exist")
    code = create_confirm_code()
    print(code)  # Для теста!
    await cache.set(
        email=user_in.email,
        # value=create_confirm_code(),
        value=code,
    )
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


@router.post("/verify")
async def verify(
    data: VerifyEmail,
    session: AsyncSession = Depends(db_helper.session_dependency),
    cache: VerificationCodesCache = Depends(get_confirm_codes_cache),
):
    key = data.email
    stored_key = await cache.get(key)
    if not stored_key:
        raise HTTPException(status_code=400, detail="Confirm code expired or invalid")
    if stored_key != data.code:
        raise HTTPException(status_code=400, detail="Invalid code")
    user = await get_user_by_username(session, data.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_verified = True
    await session.commit()
    await cache.delete(data.email)
    return {"detail": "User is verified."}


@router.post("/password_reset/request")
async def password_reset(
    email: EmailStr,
    cache: ResetCodesCache = Depends(get_reset_codes_cache),
):
    code = create_confirm_code()
    print(code)
    await cache.set(email=email, value=code)


@router.post("/password_reset/confirm")
async def password_confirm(
    data: VerifyPassword,
    cache: ResetCodesCache = Depends(get_reset_codes_cache),
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    stored_code = await cache.get(email=data.email)
    return await verify_confirm_codes_and_update_user(
        code=data.code, code_hash=stored_code, data=data, session=session
    )
