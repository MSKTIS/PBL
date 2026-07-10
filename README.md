## 概要
電気工事士資格試験の合格率向上を目的とした学習支援システムです。  

ボットに質問することで簡単な疑問を解消し、効率の良い学習が可能となります。
また、作成した部品を撮影することで、AIが作成した部品の成否を判定し、改善方法などを提示してくれます。  

※ これは大学のPBLにて作成したものです。

## 主な機能

* **シナリオ型チャットボット**: Discord Bot を利用したチャットボットシステム
* **撮影機能**: Flask, ngrok を利用したWebカメラサーバー
* **AI画像分類**: 学習済み AIモデル による画像分類

## 使用技術
#### 使用言語
* Python
#### 使用ライブラリ
* Discord.py
* Flask
* pyngrok
* PyTorch
* TorchVision
* Pillow

## インストール

必要なライブラリをインストールしてください。
```bash
pip install discord.py flask pyngrok torch torchvision pillow
```
## 初期設定

### Discord Bot
1. Discordにてアカウント登録を行なってください。
https://discord.com/login

2. Discord Developer Portal で Botを作成します。
   https://discord.com/developers/home

3. `ChatBot/DiscordBot.py` の`93行目`に作成したBotのトークンを書き込んでください。

### ngrok

カメラサーバーを外部公開するために、ngrokのアカウント登録が必要です。  

1. https://ngrok.com にてアカウントを作成してください。
2. ngrokの認証トークンを設定してください。  
```bash
ngrok config add-authtoken <authtoken>
```

## AIについて

本システムでは、事前学習済みの **EfficientNet-B0** をベースとした転移学習を行っています。

学習済みモデルは `AI/learning/model.pth` に保存されています。

分類可能なクラスは以下の4種類です。

| クラス | 状態 |
|--------|------|
| `good` | 成功 |
| `longer_between` | 線と圧着部分が長すぎる |
| `longer_trip` | 導線の先端部分が長すぎる |
| `short` | 線と圧着部分が短すぎる |

## ディレクトリ構成

```text
PBL/
├── AI/
│   ├── classfilter.py        # 画像分類処理
│   └── learning/
│       ├── train.py          # AI学習
│       ├── model.pth         # 学習済みモデル
│       └── classes.json
├── ChatBot/
│   ├── DiscordBot.py         # メインプログラム
│   ├── scenarios/
│   │   └── chatbot.json      # 会話シナリオ
│   └── WebCamera/            # カメラ画面
├── 学習素材撮影用のファイル/  # AI学習用画像撮影ツール
└── README.md
```