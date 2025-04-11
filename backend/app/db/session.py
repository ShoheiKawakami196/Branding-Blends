from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import DATABASE_URL  # 修正: settingsから直接DATABASE_URLをインポート

# データベース接続URLの設定
SQLALCHEMY_DATABASE_URL = DATABASE_URL

# データベースエンジンの作成
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,  # 接続確認のための設定（MySQL推奨）
)

# セッションローカルの設定
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# モデルのベースクラス
Base = declarative_base()

# 依存性注入用のデータベースセッション取得関数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


