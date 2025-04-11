from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.db.models.transaction import Transaction
from app.db.session import get_db
from app.core.auth import verify_token  # トークン検証関数をインポート

router = APIRouter()

def generate_comment(score: int) -> str:
    """
    スコアに基づいてコメントを生成する関数
    """
    if score >= 90:
        return "素晴らしい状態です！"
    elif score >= 75:
        return "良好な状態です。"
    else:
        return "改善が必要です。"

def scale_score_to_ten(score: int) -> int:
    """
    スコアを 100 点満点から 10 点満点に変換
    """
    return int(score / 10)  # 100点満点のスコアを10点満点に変換

@router.get("/{transaction_id}")
async def get_result(
    transaction_id: int,
    db: Session = Depends(get_db),
    authorization: str = Header(...),
):
    try:
        # トークン検証
        token = authorization.replace("Bearer ", "")
        payload = verify_token(token)

        # データベースからトランザクション情報を取得
        transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()

        if not transaction:
            raise HTTPException(status_code=404, detail="指定された結果が見つかりません")

        return {
            "user_id": transaction.user_id,
            "scores": {
                "skin_condition": {
                    "score_10": scale_score_to_ten(transaction.metric1_score),  # 10点満点スコア
                    "score_100": transaction.metric1_score,  # 100点満点スコア
                    "comment": generate_comment(transaction.metric1_score),
                },
                "hair_condition": {
                    "score_10": scale_score_to_ten(transaction.metric2_score),
                    "score_100": transaction.metric2_score,
                    "comment": generate_comment(transaction.metric2_score),
                },
                "beard_condition": {
                    "score_10": scale_score_to_ten(transaction.metric3_score),
                    "score_100": transaction.metric3_score,
                    "comment": generate_comment(transaction.metric3_score),
                },
                "total_score_100": transaction.total_score,  # トータルスコア（100点満点）
                "comment": generate_comment(transaction.total_score),
            }
        }

    except HTTPException as e:
        raise e

    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="内部サーバーエラー")

