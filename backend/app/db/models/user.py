# backend/app/db/models/user.py

from sqlalchemy import Column, Integer, String, DateTime, Text, Date
from sqlalchemy.orm import relationship
from app.db.session import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    birth_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)  # ← 最終ログイン日時を追加

    # リレーションシップ
    transactions = relationship("Transaction", back_populates="user")
    # evaluation_histories = relationship("EvaluationHistory", back_populates="user")

