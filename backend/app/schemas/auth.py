from pydantic import BaseModel
from datetime import date

class UserCreate(BaseModel):
    user_id: str  # ユーザーID
    email: str    # メールアドレス
    password: str # パスワード
    birth_date: date  # ← 追加

class UserLogin(BaseModel):
    user_id: str
    password: str