from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# FastAPIアプリケーションのインスタンスを作成
app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://branding-ngrok-app.ngrok.io", "https://app-002-step3-2-node-oshima4.azurewebsites.net"],  # Azureから受けられるように変更
    allow_credentials=True,
    allow_methods=["*"],  # 必要なHTTPメソッド（例: GET, POST, OPTIONS）
    allow_headers=["*"],  # 必要なHTTPヘッダー（例: Content-Type, Authorization）
)

# ルーターのインポートと登録
from app.api.endpoints import upload, result, auth

app.include_router(upload.router, prefix="/upload", tags=["UploadAndEvaluation"])
app.include_router(result.router, prefix="/result", tags=["ResultConfirmation"])
app.include_router(auth.router, prefix="/auth", tags=["UserCertification"])
# app.include_router(score.router, prefix="/score", tags=["Score"])
# app.include_router(user.router, prefix="/user", tags=["User"])

# 起動確認用のエンドポイント
@app.get("/")
def read_root():
    return {"message": "FastAPIアプリケーションが起動しました！"}
