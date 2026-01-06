import datetime
import os

import jwt
from fastapi import HTTPException
from passlib.context import CryptContext

hashed_content = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


def create_jwt_token(user_id: int):
    now = datetime.datetime.now()
    exp = now + datetime.timedelta(minutes=15)
    payload = {
        "sub": user_id,
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
