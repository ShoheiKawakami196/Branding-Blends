
---

# Branding-Blends

## Branding_Brends_Backend

肌状態と髪の清潔感をAIで自動評価するWebアプリのバックエンドです。  
ユーザーがアップロードした顔画像から、AIが3つの観点（肌、髪、髭）をスコアリングし、結果を返却・保存します。

---

### 🧠 このプロジェクトでやっていること

#### 1. 学習済みモデルの活用

本アプリは、PyTorchで学習した以下の分類モデルを活用しています：

| モデル                  | 分類内容                     | 使用手法                     | 備考                                |
|-------------------------|------------------------------|------------------------------|-------------------------------------|
| Skin Classifier         | 肌質（乾燥肌・脂性肌・普通肌） | CNN（畳み込みニューラルネットワーク） | データ拡張あり                     |
| Hair Cleanliness Classifier | 髪の清潔感（清潔 / 非清潔）   | 転移学習（ResNet18）          | データ不均衡に対応、交差検証あり   |

モデル学習は、FastAPIのプロジェクトとは別のローカルリポジトリで学習を行い、`pth` (PyTorch)形式のファイルを出力しています。  
これらのモデルは `.pth` ファイルとして `backend/models/` に保存されており、FastAPI のエンドポイントに組み込まれています。  

ただし、`pth` のファイルは容量が重いので、`.gitignore` で除外しています。必要に応じて開示します。  
また、`pth` 形式のファイルは容量が重く、デプロイにはDockerが必須になります。今回のプロジェクトではDockerの学習や導入コストを低減するため、ngrokのトンネリングサービスを用いてエンドポイントを安全に公開化します。

---

#### 2. FastAPIでの推論エンドポイント

ユーザーの顔画像を受け取り、以下の処理を行う `/upload` エンドポイントを提供しています：

1. 顔領域の検出・クロッピング（`face_recognition` 使用）  
2. 学習済みモデルによる肌・髪の分類  
3. 髭は現状ダミースコア（80点）を返す仕様  
4. 各スコアと合計スコアの計算  
5. 画像とスコアをDBに保存（SQLAlchemy）  

レスポンスとして、`transaction_id` を返します。

---

### 🔧 ディレクトリ構成と主な役割

```
backend/
├── app/               # FastAPI本体のコード群
│   ├── api/           # APIエンドポイント定義（upload, result, auth）
│   ├── core/          # アプリの設定や認証処理（JWT検証など）
│   ├── db/            # DB接続・モデル定義・CRUD操作
│   ├── schemas/       # Pydanticによるリクエスト/レスポンス定義
│   └── main.py        # FastAPI起動スクリプト（エントリーポイント）
│
├── models/            # 学習済みモデルの保存場所（.pthファイル）　github未連携
│   ├── skin_classifier_model.pth
│   ├── hair_classifier_cleanliness.pth
│   └── beard_classifier.pth（※未使用）
│
├── requirements.txt   # 使用ライブラリ一覧
└── .env               # 環境変数（APIキーやDB接続文字列など）
```

---

### ⚙️ モデル学習からAPIへの統合までの流れ

#### 1. 肌分類モデル（SkinClassifierCNN）
- **3クラス分類**: `oily`, `dry`, `normal`  
- **データ拡張＋CNNベース**  
- `.pth` に保存して `models/skin_classifier_model.pth` へ配置  

```python
model = SkinClassifierCNN()
model.load_state_dict(torch.load("models/skin_classifier_model.pth"))
```

#### 2. 髪分類モデル（ResNet18ベース）
- **2クラス分類**: `clean / not_clean`  
- **転移学習**: ResNet18 ＋ アーリーストッピング  
- **クラス不均衡対応**: 重みづけ  
- `models/hair_classifier_cleanliness.pth` として保存  

```python
hair_model = models.resnet18(pretrained=False)
hair_model.fc = nn.Sequential(...)
hair_model.load_state_dict(torch.load("models/hair_classifier_cleanliness.pth"))
```

---

### 📌 備考

- `beard_classifier.pth` は現時点で未使用です（今後拡張予定）。  
- 顔検出には dlib ベースの `face_recognition` を利用しています。  

---
