# backend/app/db/models/transaction.py

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)  # 自動インクリメントを追加
    user_id = Column(String(50), ForeignKey("users.user_id"), nullable=False)
    image_path = Column(String(255), nullable=True)  # 画像データへのパス
    metric1_score = Column(Float, nullable=True)
    metric2_score = Column(Float, nullable=True)
    metric3_score = Column(Float, nullable=True)
    total_score = Column(Float, nullable=True)
    evaluated_at = Column(DateTime, nullable=False)

    # positive_comment_id = Column(Integer, ForeignKey("positive_comments.id"), nullable=True)
    # advice_comment_id = Column(Integer, ForeignKey("advice_comments.id"), nullable=True)

    # リレーションシップ
    user = relationship("User", back_populates="transactions")
    # positive_comment = relationship("PositiveComment", back_populates="transactions")
    # advice_comment = relationship("AdviceComment", back_populates="transactions")


