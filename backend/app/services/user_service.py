from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt

from app.models.user import User
from app.schemas.user import UserCreate
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"

def get_user_by_email(db: Session, email: str) -> User:
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> User:
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: UserCreate) -> User:
    if get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = pwd_context.hash(user.password)
    db_user = User(email=user.email, username=user.username, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str) -> User:
    user = get_user_by_email(db, email)
    if not user or not pwd_context.verify(password, user.password_hash):
        return None
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt