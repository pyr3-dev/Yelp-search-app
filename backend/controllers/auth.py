from fastapi import HTTPException, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from schema import RegisterForm, User as UserSchema
from services.auth import jwtSign, jwtSignRefresh, jwtVerifyRefresh, validatePassword
from services.user import create_user, get_user_by_email

REFRESH_COOKIE_MAX_AGE = 60 * 60 * 24 * 30


def _set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key="refresh_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=REFRESH_COOKIE_MAX_AGE,
        path="/",
    )


async def login_controller(
    db: Session,
    response: Response,
    form_data: OAuth2PasswordRequestForm,
) -> dict:
    user = get_user_by_email(db, form_data.username)
    if not user or not validatePassword(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user_schema = UserSchema(id=user.id, email=user.email, password="")
    _set_refresh_cookie(response, jwtSignRefresh(user_schema))
    return {"access_token": jwtSign(user_schema), "token_type": "bearer"}


async def register_controller(db: Session, data: RegisterForm) -> dict:
    user = create_user(db, data.email, data.password)
    return {"id": user.id, "email": user.email}


async def refresh_controller(request: Request, response: Response) -> dict:
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="Missing refresh token")
    user = jwtVerifyRefresh(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    _set_refresh_cookie(response, jwtSignRefresh(user))
    return {"access_token": jwtSign(user), "token_type": "bearer"}


async def logout_controller(response: Response) -> dict:
    response.delete_cookie(key="refresh_token", path="/")
    return {"ok": True}
