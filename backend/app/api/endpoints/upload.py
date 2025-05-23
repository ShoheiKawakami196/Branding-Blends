# FastAPIのルーター機能を利用
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, Header
import cv2
import numpy as np
import face_recognition
import torch
from torchvision import transforms, models
import torch.nn as nn
import torch.nn.functional as F
from datetime import datetime
import os
from PIL import Image  # 画像をPIL形式に変換して正規化処理で利用
from sqlalchemy.orm import Session
from app.db.models.transaction import Transaction
from app.db.session import get_db
from app.core.auth import verify_token  # トークン検証関数をインポート

router = APIRouter()

# 保存先ディレクトリとモデルパスの設定
SAVE_DIR = "saved"
MODEL_DIR = "models"
os.makedirs(SAVE_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

# 肌状態分類用のCNNモデル定義：学習済みモデルアーキテクチャ定義（学習時と同じ構造）
class SkinClassifierCNN(nn.Module):
    def __init__(self, num_classes=3):  # クラス数は3（oily, dry, normal）
        super(SkinClassifierCNN, self).__init__()
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(128 * 28 * 28, 512)
        self.fc2 = nn.Linear(512, num_classes)
        self.dropout = nn.Dropout(0.5)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = self.pool(F.relu(self.conv3(x)))
        x = x.view(-1, 128 * 28 * 28)
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x

# class HairClassifierCNN(nn.Module)→当初使用していたモデル定義はコメントアウト
#     # def __init__(self, num_classes=3):  # クラス数は3（Curly Hair, Wavy Hair, Straight Hair）
#     def __init__(self, num_classes=2):  # ★変更点: クラス数を2に設定（清潔感あり/なし）
#         super(HairClassifierCNN, self).__init__()
#         self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
#         self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
#         self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
#         self.pool = nn.MaxPool2d(2, 2)
#         self.fc1 = nn.Linear(128 * 28 * 28, 512)
#         self.fc2 = nn.Linear(512, num_classes)
#         self.dropout = nn.Dropout(0.5)

#     def forward(self, x):
#         x = self.pool(F.relu(self.conv1(x)))
#         x = self.pool(F.relu(self.conv2(x)))
#         x = self.pool(F.relu(self.conv3(x)))
#         x = torch.flatten(x, start_dim=1)  # Flatten for fully connected layers
#         x = F.relu(self.fc1(x))
#         x = self.dropout(x)
#         return self.fc2(x)

# 肌状態分類用のCNNモデル定義：ResNet-18ベースの転移学習モデルを定義（★変更点: HairClassifierCNNをコメントアウトにて削除）
hair_model = models.resnet18(pretrained=False)  # 事前学習済みモデルは不要
num_features = hair_model.fc.in_features  # 最終層の入力サイズを取得
hair_model.fc = nn.Sequential(
    nn.Linear(num_features, 512),  # ★修正: 保存時と同じサイズに戻す
    nn.ReLU(),
    nn.Dropout(0.5),
    nn.Linear(512, 2)  # 清潔感：2クラス分類（clean / not_clean）
)


# class SimpleBeardClassifierCNN(nn.Module):髭状態分類用モデルは将来的に作成
#     def __init__(self, num_classes=2):  # クラス数は2（beard, no_beard）
#         super(SimpleBeardClassifierCNN, self).__init__()
#         self.conv1 = nn.Conv2d(3, 32, kernel_size=3)
#         self.conv2 = nn.Conv2d(32, 64, kernel_size=3)
#         self.pool = nn.MaxPool2d(2, 2)
#         # 修正: fc1の入力サイズを64 * 54 * 54に変更
#         self.fc1 = nn.Linear(64 * 54 * 54, 128)  
#         self.fc2 = nn.Linear(128, num_classes)

#     def forward(self, x):
#         x = self.pool(F.relu(self.conv1(x)))
#         x = self.pool(F.relu(self.conv2(x)))
#         x = x.view(-1, 64 * 54 * 54)  
#         x = F.relu(self.fc1(x))
#         return self.fc2(x)

# モデル初期化と重み読み込み
skin_model = SkinClassifierCNN(num_classes=3).cpu()
hair_model = hair_model.cpu()  # CPUで動作するよう設定
# beard_model = SimpleBeardClassifierCNN(num_classes=2).cpu()

# 学習済み重みのロード
skin_model.load_state_dict(torch.load(os.path.join(MODEL_DIR, "skin_classifier_model.pth"), map_location="cpu"))
hair_model.load_state_dict(torch.load(os.path.join(MODEL_DIR, "hair_classifier_cleanliness.pth"), map_location="cpu"))# ★変更点: 正しいファイル名を指定してロード（清潔感判定モデル）
# beard_model.load_state_dict(torch.load(os.path.join(MODEL_DIR, "beard_classifier.pth"), map_location="cpu"))

skin_model.eval()
hair_model.eval()
# beard_model.eval()

# 川上追記: データ前処理はtorchvisionのComposeで統一
data_transforms = transforms.Compose([
    transforms.Resize((224, 224)),# モデル入力サイズに合わせてリサイズ
    transforms.ToTensor(),# テンソル変換
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])# 正規化（ImageNetの平均値・標準偏差）
])

# スコア対応表（分類結果に応じてスコア化）
SKIN_CLASS_TO_SCORE = {
    "oily": 70,
    "dry": 80,
    "normal": 100,
}

# クラス名とスコア対応表（★変更点: 清潔感あり/なしに対応）
HAIR_CLASS_TO_SCORE = {
    "not_clean": 70,
    "clean": 100,
}

BEARD_CLASS_TO_SCORE = {
    "beard": 50,
    "no_beard": 100,
}

@router.post("/")  # エンドポイントはルート（"/"）として定義
async def upload_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),  # データベースセッションを取得
    authorization: str = Header(...),  # Authorizationヘッダーからトークンを取得
):
    try:
        print(f"Authorization header received: {authorization}")

        # JWTトークン検証とユーザーIDの取得
        token = authorization.replace("Bearer ", "")
        payload = verify_token(token)
        print(f"Token payload: {payload}")
        
        user_id = payload["sub"]
        print(f"User ID from token: {user_id}")

        # ファイル内容を読み込みOpenCVでデコード
        contents = await file.read()
        np_arr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        # 顔検出（RGB変換 → face_recognitionで検出）
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        faces = face_recognition.face_locations(rgb_img)

        if not faces:
            return {"error": "顔を検出できませんでした"}

        # 顔の範囲を拡大して切り取り
        top, right, bottom, left = faces[0]
        height = bottom - top
        width = right - left

        margin_top = int(height * 0.6)     # 上に40%拡張（髪の毛）
        margin_bottom = int(height * 0.2)  # 下に20%
        margin_side = int(width * 0.2)     # 左右に20%

        img_height, img_width, _ = img.shape
        new_top = max(0, top - margin_top)
        new_bottom = min(img_height, bottom + margin_bottom)
        new_left = max(0, left - margin_side)
        new_right = min(img_width, right + margin_side)

        face_img = img[new_top:new_bottom, new_left:new_right]
        face_img_resized = cv2.resize(face_img, (224, 224))  # モデル入力サイズに合わせてリサイズ

        # 画像保存処理追加
        filename = f"face_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        filepath = os.path.join(SAVE_DIR, filename)
        cv2.imwrite(filepath, face_img_resized)

        # Tensor変換と正規化
        # tensor_img = torch.tensor(face_img_resized).permute(2, 0, 1).float() / 255.0
        pil_image = Image.fromarray(cv2.cvtColor(face_img_resized, cv2.COLOR_BGR2RGB))
        tensor_img = data_transforms(pil_image).unsqueeze(0)  # ★修正: 統一されたデータ前処理を適用

        # 推論処理
        with torch.no_grad():
            skin_output = skin_model(tensor_img)
            hair_output = hair_model(tensor_img)

            # ソフトマックスで確率化
            skin_probabilities = torch.softmax(skin_output, dim=1)[0].tolist()
            hair_probabilities = torch.softmax(hair_output, dim=1)[0].tolist()

        # クラス名リスト
        skin_classes = ["oily", "dry", "normal"]
        # （★変更点: 清潔感あり/なしに対応）
        hair_classes = ["not_clean", "clean"]

        # 出力確率と対応するクラス名を表示
        for i, prob in enumerate(skin_probabilities):
            print(f"Class: {skin_classes[i]}, Probability: {prob:.4f}")

        for i, prob in enumerate(hair_probabilities):
            print(f"Class: {hair_classes[i]}, Probability: {prob:.4f}")

        # 肌状態スコア計算
        skin_class_index = skin_probabilities.index(max(skin_probabilities))
        predicted_skin_class = skin_classes[skin_class_index]
        skin_score = int(SKIN_CLASS_TO_SCORE[predicted_skin_class])
        print(f"Predicted class: {predicted_skin_class}, Score: {skin_score}")

        # 髪状態スコア計算
        hair_class_index = hair_probabilities.index(max(hair_probabilities))
        predicted_hair_class = hair_classes[hair_class_index]
        hair_score_raw = max(70, hair_probabilities[hair_class_index] * HAIR_CLASS_TO_SCORE[predicted_hair_class])
        hair_score_finalized = int(round(hair_score_raw))  # 小刻みなスコア化
        print(f"hair_probabilities: {hair_probabilities}, Predicted class: {predicted_hair_class}, Score: {hair_score_finalized}")

        # 髭状態スコア計算（ダミーデータとして固定値）
        beard_score = 80  # ダミースコア（後でモデル推論に置き換え可能）

        # トータルスコア計算
        total_score = int((skin_score + hair_score_finalized + beard_score) // 3)

         # データベース保存処理を追加（必要な箇所のみ変更）
        transaction= Transaction(
              user_id=user_id,
              image_path=filepath,
              metric1_score=int(skin_score),
              metric2_score=int(hair_score_finalized),
              metric3_score=int(beard_score),
              total_score=int(total_score),
              evaluated_at=datetime.now(),
          )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)

        return {"transaction_id":transaction.id}

    except HTTPException as e:
         print(f"HTTPエラー発生:{e}")
         raise e

    except Exception as e:
         print(f"予期しないエラー発生:{e}")
         raise HTTPException(status_code=500, detail="内部サーバーエラー")
