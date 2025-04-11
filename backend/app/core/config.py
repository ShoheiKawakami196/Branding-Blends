import os
from dotenv import load_dotenv

# .envファイルの読み込み
load_dotenv()

# データベース接続情報
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')  # デフォルト値を設定
DB_PORT = os.getenv('DB_PORT')       # デフォルト値を設定
DB_NAME = os.getenv('DB_NAME')

# MySQLのURL構築
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

