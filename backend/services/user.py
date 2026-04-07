from sqlalchemy.orm import Session

from models import User
from schema import User as UserSchema
from services.auth import hashPassword


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> UserSchema | None:
    user = db.query(User).filter(User.email == email).first()
    return UserSchema(**user.__dict__) if user else None


def create_user(db: Session, email: str, password: str) -> UserSchema:
    db_user = User(email=email, password=hashPassword(password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return UserSchema(**db_user.__dict__)
