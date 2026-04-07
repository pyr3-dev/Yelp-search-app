import os
from datetime import datetime, timedelta, timezone

import bcrypt
from dotenv import load_dotenv
import jwt
from schema import User as UserSchema

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

JWT_SECRET = os.getenv("JWT_SECRET", "your_jwt_secret_key")
REFRESH_SECRET = os.getenv("REFRESH_SECRET", "your_refresh_secret_key")


def validatePassword(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def hashPassword(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def jwtSign(user: UserSchema) -> str:
    payload = {
        "id": user.id,
        "email": user.email,
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def jwtVerify(token: str) -> UserSchema | None:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        if payload.get("type") != "access":
            return None
        return UserSchema(id=payload["id"], email=payload["email"], password="")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def jwtSignRefresh(user: UserSchema) -> str:
    payload = {
        "id": user.id,
        "email": user.email,
        "type": "refresh",
        "exp": datetime.now(timezone.utc) + timedelta(days=30),
    }
    return jwt.encode(payload, REFRESH_SECRET, algorithm="HS256")


def jwtVerifyRefresh(token: str) -> UserSchema | None:
    try:
        payload = jwt.decode(token, REFRESH_SECRET, algorithms=["HS256"])
        if payload.get("type") != "refresh":
            return None
        return UserSchema(id=payload["id"], email=payload["email"], password="")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
