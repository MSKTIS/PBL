import json

import torch
import torch.nn as nn
from PIL import Image
from torchvision import models, transforms

# デバイス設定
if torch.backends.mps.is_available():
    device = torch.device("mps")

elif torch.cuda.is_available():
    device = torch.device("cuda")

else:
    device = torch.device("cpu")


# クラス名
with open("learning/classes.json", "r") as f:
    classes = json.load(f)
num_classes = len(classes)


# EfficientNetモデルを使用
model = models.efficientnet_b0()

# 線形変換
model.classifier[1] = nn.Linear(model.classifier[1].in_features, len(classes))

# 学習させたモデルの読み込み
model = model.to(device)
model.load_state_dict(torch.load("learning/model.pth", map_location=device))
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

        # それぞれの確率
        for i, p in enumerate(prob):
            print(f"{classes[i]:15s}: {p.item():.2%}")

        # 分類結果とその確率
        index = prob.argmax().item()
        confidence = prob[index].item()

        return classes[index], confidence


result, confidence = predict("test.png")

print(f"予測結果: {result}")
print(f"信頼度: {confidence:.2%}")
