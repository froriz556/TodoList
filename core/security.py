import datetime
import os

import jwt
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import db_helper
from core.models.users import User

hashed_content = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def create_jwt_token(user_id: int):
    now = datetime.datetime.now(datetime.timezone.utc)
    exp = now + datetime.timedelta(minutes=15)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": exp,
    }
    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def decode_jwt_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def get_user_id_by_token(token: str):
    try:
        payload = decode_jwt_token(token)
        return payload.get("sub")
    except:
        raise HTTPException(status_code=403, detail="Forbidden")


def create_password_hash(password: str) -> str:
    return hashed_content.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return hashed_content.verify(password, password_hash)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> User:
    payload = decode_jwt_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid Token")
    user = await session.get(User, int(user_id))
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user
