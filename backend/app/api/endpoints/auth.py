from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from app.db.crud.user import create_user, get_user_by_user_id, verify_password
from app.schemas.auth import UserCreate, UserLogin
from app.core.auth import create_access_token, verify_token
from app.db.session import get_db

router = APIRouter()

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = create_user(db, user)
    return {"message": "ユーザー登録成功", "user_id": db_user.user_id}

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    print(f"Received user_id: {user.user_id}, password: {user.password}")  # 入力値をログ出力
    db_user = get_user_by_user_id(db, user.user_id)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="ユーザーIDまたはパスワードが間違っています")
    
    token = create_access_token({"sub": db_user.user_id})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/protected")
def protected_route(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="無効なトークンです")
    
    return {"message": f"{payload['sub']} さん、ようこそ！"}
