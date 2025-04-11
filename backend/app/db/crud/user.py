from fastapi import HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.db.models.user import User
from app.schemas.auth import UserCreate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def create_user(db: Session, user: UserCreate):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="このメールアドレスは既に登録されています")
    if db.query(User).filter(User.user_id == user.user_id).first():
        raise HTTPException(status_code=400, detail="このユーザーIDは既に使用されています")

    hashed_password = get_password_hash(user.password)
    db_user = User(
        user_id=user.user_id,
        email=user.email,
        hashed_password=hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_user_id(db: Session, user_id: str):
    return db.query(User).filter(User.user_id == user_id).first()
