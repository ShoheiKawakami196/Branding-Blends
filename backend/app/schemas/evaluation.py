from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EvaluationCreate(BaseModel):
    """
    新しい評価を作成する際に使用するスキーマ。
    """
    user_id: int
    skin_score: float
    hair_score: float
    beard_score: float
    total_score: float
    positive_comment_id: Optional[int] = None
    advice_comment_id: Optional[int] = None

class EvaluationResponse(BaseModel):
    """
    APIレスポンスとして返却される評価結果のスキーマ。
    """
    id: int
    user_id: int
    skin_score: float
    hair_score: float
    beard_score: float
    total_score: float
    created_at: datetime

    class Config:
        orm_mode = True  # ORMとの互換性を有効化（SQLAlchemyモデルとの連携）
