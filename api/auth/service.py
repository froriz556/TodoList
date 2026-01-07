from fastapi import HTTPException
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.schemas import UserCreate, UserLogin
from core.models.users import User
from core.security import (
    get_user_id_by_token,
    hashed_content,
    verify_password,
    create_jwt_token,
)


async def get_user_by_id_with_token(session: AsyncSession, token: str) -> User | None:
    user_id = get_user_id_by_token(token)
    return await session.get(User, user_id)


async def get_user_by_username(
    session: AsyncSession, username: EmailStr
) -> User | None:
    result = await session.execute(select(User).where(User.email == username))
    return result.scalar_one_or_none()


async def create_new_user(session: AsyncSession, user_in: UserCreate):
    user_password = hashed_content.hash(user_in.password)
    new_user = User(email=user_in.email, password_hash=user_password)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user


async def authenticate(session: AsyncSession, user_in: UserLogin):
    user = await get_user_by_username(session, user_in.email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not verify_password(password=user_in.password, password_hash=user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return create_jwt_token(user.id, token_type="access")


async def create_refresh_token(session: AsyncSession, user_in: UserLogin):
    user = await get_user_by_username(session=session, username=user_in.email)
    return create_jwt_token(user.id, time_in_minutes=10080, token_type="refresh")
