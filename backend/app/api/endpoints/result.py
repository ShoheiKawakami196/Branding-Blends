from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.db.models.transaction import Transaction
from app.db.session import get_db
from app.core.auth import verify_token  # トークン検証関数をインポート
import random

router = APIRouter()

def generate_comment(score: int) -> str:
    """
    スコアに基づいてランダムなコメントを生成する関数
    """
    if score >= 90:
        comments = [
            "素晴らしい状態です！",
            "完璧です！これからもこの調子で！",
            "とても良い状態ですね！",
            "最高のコンディションです！",
            "理想的な状態を保っていますね！",
            "素晴らしい成果です！自信を持ってください！",
            "とても健康的な状態です！",
            "素晴らしい結果です！これからも頑張りましょう！",
            "理想的な状態ですね！素敵です！",
            "完璧な状態です！"
        ]
    elif score >= 75:
        comments = [
            "良好な状態です。",
            "健康的な状態を保っていますね！",
            "とてもいい感じです！",
            "順調な状態ですね！この調子で続けましょう。",
            "安定したコンディションです。",
            "良い結果が出ていますね！",
            "健康的でバランスの取れた状態です。",
            "とても良い状態ですね、引き続き頑張りましょう。",
            "いい感じの結果ですね！努力が報われています。",
            "良好な状態を維持していますね！"
        ]
    else:
        comments = [
            "少し改善の余地がありますね。一緒に頑張りましょう！",
            "大丈夫です。少しケアを増やしてみましょう！",
            "改善のチャンスです！ポジティブに取り組みましょう！",
            "焦らず、少しずつ改善していきましょう。",
            "努力次第でさらに良くなりますよ！",
            "少しケアを意識してみると良いかもしれません。",
            "ポジティブに考えて、次のステップに進みましょう。",
            "改善する余地がありますが、可能性は十分ありますよ！",
            "小さな変化が大きな結果につながります。頑張りましょう！",
            "これからもっと良くなるはずです。一緒に進んでいきましょう！"
        ]
    
    # コメントをランダムに選択して返す
    return random.choice(comments)



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

