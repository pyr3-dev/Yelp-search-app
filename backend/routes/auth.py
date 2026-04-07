from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from controllers.auth import (
    login_controller,
    logout_controller,
    refresh_controller,
    register_controller,
)
from dependencies import get_db
from schema import RegisterForm

router = APIRouter()


@router.post("/login")
async def login(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
):
    return await login_controller(db, response, form_data)


@router.post("/register")
async def register(
    data: Annotated[RegisterForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
):
    return await register_controller(db, data)


@router.post("/refresh")
async def refresh(request: Request, response: Response):
    return await refresh_controller(request, response)


@router.post("/logout")
async def logout(response: Response):
    return await logout_controller(response)
