import os

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms

# 設定
BATCH_SIZE = 16
EPOCHS = 10
LR = 0.0001

# Mac Apple Silicon用
if torch.backends.mps.is_available():
    device = torch.device("mps")

# NVIDIA GPU用
elif torch.cuda.is_available():
    device = torch.device("cuda")

# CPU
else:
    device = torch.device("cpu")

print("device:", device)


# データ調整の用の関数群
train_transform = transforms.Compose(
    [
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ]
)


# データセット調整
dataset = datasets.ImageFolder("dataset", transform=train_transform)
# データセット読み込み
loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)
print("classes:", dataset.classes)


# モデル読み込み
model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.DEFAULT)
num_classes = len(dataset.classes)

# 最後の分類層変更
model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)

model = model.to(device)


# 損失関数
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=LR)


# 学習
for epoch in range(EPOCHS):
    model.train()

    running_loss = 0.0
    correct = 0
    total = 0

    for images, labels in loader:
        # デバイス用に調整
        images = images.to(device)
        labels = labels.to(device)

        # 推論
        outputs = model(images)
        # 損失
        loss = criterion(outputs, labels)
        # 初期化
        optimizer.zero_grad()
        # 逆伝播
        loss.backward()
        # 更新
        optimizer.step()

        running_loss += loss.item()

        # 精度計算
        _, predicted = outputs.max(1)

        total += labels.size(0)

        correct += predicted.eq(labels).sum().item()

    acc = 100 * correct / total

    print(f"Epoch [{epoch + 1}/{EPOCHS}] Loss: {running_loss:.4f} Accuracy: {acc:.2f}%")


# 保存
torch.save(model.state_dict(), "model.pth")
print("model saved")
