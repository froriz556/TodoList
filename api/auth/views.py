from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.schemas import UserCreate, UserLogin, UserResponse
from api.auth.service import get_user_by_username, create_new_user, authenticate
from core.models import db_helper

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


@router.post("/login", response_model=None)
async def login(
    user_in: UserLogin,
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    token = await authenticate(session=session, user_in=user_in)
    return {"access_token": token}
