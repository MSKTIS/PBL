import json
import os

import torch
import torch.nn as nn
from PIL import Image
from torchvision import models, transforms

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# デバイス設定
if torch.backends.mps.is_available():
    device = torch.device("mps")

elif torch.cuda.is_available():
    device = torch.device("cuda")

else:
    device = torch.device("cpu")


# クラス名
with open(
    os.path.join(BASE_DIR, "learning", "classes.json"), "r", encoding="utf-8"
) as f:
    classes = json.load(f)
num_classes = len(classes)


# EfficientNetモデルを使用
model = models.efficientnet_b0()

# 線形変換
model.classifier[1] = nn.Linear(model.classifier[1].in_features, len(classes))

# 学習させたモデルの読み込み
model = model.to(device)
model.load_state_dict(
    torch.load(
        os.path.join(BASE_DIR, "learning", "model.pth"),
        map_location=device,
    )
)
model.eval()

# 画像変換
transform = transforms.Compose(
    [
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ]
)


def predict(path):
    # 推論
    image = Image.open(path).convert("RGB")
    x = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        y = model(x)
        # 活性化
        prob = torch.softmax(y, dim=1)[0]

        # 分類結果とその確率
        index = prob.argmax().item()
        confidence = prob[index].item()

        return {"class": classes[index], "confidence": confidence}
