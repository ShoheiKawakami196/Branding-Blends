from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import cv2
import numpy as np
import face_recognition
import os

app = FastAPI()

# CORS設定（フロントから呼べるように）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 必要に応じて限定
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    contents = await file.read()
    np_arr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    faces = face_recognition.face_locations(rgb_img)

    if faces:
        top, right, bottom, left = faces[0]
        face_img = img[top:bottom, left:right]
        face_img = cv2.resize(face_img, (128, 128))

        filename = f"face_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        os.makedirs("saved", exist_ok=True)
        filepath = os.path.join("saved", filename)
        cv2.imwrite(filepath, face_img)

        return {"message": f"顔を保存しました: {filename}"}
    else:
        return {"message": "顔が見つかりませんでした"}