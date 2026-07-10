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

## 実行
```bash
python ChatBot/DiscordBot.py
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


# AI学習
#### 学習素材撮影
次のコマンドを実行してください。
```bash
python 学習素材撮影用のファイル/server.py
```

以下のような結果が出力されると思います。
```bash
 * Serving Flask app 'server'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on https://127.0.0.1:8000
 * Running on https://<IPアドレス>:8000
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 134-619-482
```
実行機と**同じWi-Fiで接続したスマホ**で`https://<IPアドレス>:8000`のページへ飛んでください。  
警告が出ると思われますが、無視して進んでください。これで撮影を行えます。  
撮影した画像はスマホのローカルに保存されます。  

#### AIモデル作成
`AI/learning`の下に`dataset`フォルダを作成してください。
そこにクラス毎にフォルダを作成し、学習画像を配置してください。
次のコマンドを実行し、AIの学習を開始します。
```bash
python AI/learning/train.py
```
作成されたモデル`model.path`が`AI/learning`フォルダの中に作成され、`classes.json`が更新されます。

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