from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import DATABASE_URL
from pathlib import Path

# データベース接続URLの設定
SQLALCHEMY_DATABASE_URL = DATABASE_URL

# base_path を定義 (現在のファイルの3つ上の親ディレクトリを指定)
base_path = Path(__file__).resolve().parent.parent.parent

# SSL証明書（Azure 用）のパス (base_pathの直下に配置されていると仮定)
# 例: /backend/DigiCertGlobalRootCA.crt.pem
ssl_cert_path = base_path / 'DigiCertGlobalRootCA.crt.pem'
ssl_cert = str(ssl_cert_path)

# ファイルが存在するかどうかのチェック（任意）
if not ssl_cert_path.is_file():
    print(f"WARNING: Certificate file not found at the specified path: {ssl_cert}")
    # 必要であればここでエラー処理を行う

# データベースエンジンの作成
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "ssl": {"ca": ssl_cert}
    }
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



