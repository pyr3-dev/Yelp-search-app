from typing import Annotated, Generator

from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import SessionLocal
from schema import User as UserSchema
from services.auth import jwtVerify

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> UserSchema:
    user = jwtVerify(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user


