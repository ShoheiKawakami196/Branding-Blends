from pydantic import BaseModel

class UserCreate(BaseModel):
    user_id: str  # ユーザーID
    email: str    # メールアドレス
    password: str # パスワード

class UserLogin(BaseModel):
    user_id: str
    password: str