import atexit
import json
import os
import sys
import threading
import time

import discord
from discord.ext import commands
from flask import Flask, render_template, request
from pyngrok import ngrok

# from ../AI/.  import classFile する処理
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

AI_DIR = os.path.join(BASE_DIR, "..", "AI")

sys.path.insert(0, AI_DIR)

from classfilter import predict

# カメラサーバー作成
# flaskとngrokを使用する。
cameraServer = cameraServer = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "WebCamera"),
    static_folder=os.path.join(BASE_DIR, "WebCamera", "static"),
)


@cameraServer.route("/")
def index():
    user_id = request.args.get("user_id")
    return render_template("index.html", user_id=user_id)


# めっちゃ大事
# ユーザーid毎に画像を保存する辞書配列
user_images = {}

# 撮影画像の設置場所
SAVE_DIR = os.path.join(BASE_DIR, "..", "AI", "classFilter_image")
SAVE_DIR = os.path.abspath(SAVE_DIR)
os.makedirs(SAVE_DIR, exist_ok=True)


# 撮影画像を保存
@cameraServer.route("/upload", methods=["POST"])
def upload():
    user_id = request.form["user_id"]
    image = request.files["image"]

    # ユーザーid毎に名前決定
    path = os.path.join(SAVE_DIR, f"{user_id}.png")

    image.save(path)

    user_images[user_id] = path

    return "OK", 200


# プログラム終了時にに撮影した画像は全削除
def cleanup():
    for file in os.listdir(SAVE_DIR):
        path = os.path.join(SAVE_DIR, file)
        if os.path.isfile(path):
            os.remove(path)


atexit.register(cleanup)


# flaskのポート数などを設定する関数
def run_flask():
    cameraServer.run(host="0.0.0.0", port=5001)


# flaskを接続 ( 並列処理 )
threading.Thread(target=run_flask, daemon=True).start()
# Flaskの起動待ち
time.sleep(2)

# ngrokで、公開用URLを作成
public_url = ngrok.connect(5001).public_url
print(f"URL: {public_url}")


# *** discord ボットの処理 ***

# Botの個別番号
# 本番ではDiscord Botのトークンを入れよう
TOKEN = "KoreHaNisemonoNoToken"

# Botに読み取り権限を付与する
intents = discord.Intents.default()
intents.message_content = True

# discordボット作成
bot = commands.Bot(command_prefix="!", intents=intents)

# 会話データ
# JSON形式の会話データを読み込み
CHATBOT_JSON = os.path.join(BASE_DIR, "scenarios", "chatbot.json")
with open(CHATBOT_JSON, "r", encoding="utf-8") as f:
    chatbot_data = json.load(f)
# id別の会話データ
Nodes = {node["id"]: node for node in chatbot_data["chat"]}

# start以外に「最初の会話に戻る」ボタンを追加
for node_id, node in Nodes.items():
    if node_id == "start":
        continue

    # optionsがあるものにはボタンを追加
    if "options" in node:
        node["options"].append({"text": "最初の会話に戻る", "next_id": "start"})


# discord ボタン機能
# ボタンを押されると、次の会話とボタンを作成するため、再帰的な処理である
class ChatbotView(discord.ui.View):
    # 初期化
    def __init__(self, options):
        super().__init__(timeout=None)
        # id別にボタンを作る
        for i, option in enumerate(options):
            button = discord.ui.Button(
                label=option["text"], custom_id=f"{option['next_id']}_{i}"
            )
            # ボタンが押されたときの処理
            button.callback = self.button_callback
            self.add_item(button)

    # ボタンが押されたときの処理
    async def button_callback(self, interaction: discord.Interaction):
        # 押されたボタンのidを取得
        button = interaction.data["custom_id"]
        next_id = button.rsplit("_", 1)[0]

        # AIで分類する時の会話
        if next_id == "predict":
            user_id = str(interaction.user.id)

            # ユーザーの番号がない場合に撮影していないとみなす。
            # 前回の画像を分類する可能性はあり
            if user_id not in user_images:
                await interaction.response.send_message(
                    "先に撮影してね。",
                    ephemeral=True,
                )
                return

            # 撮影した画像
            image_path = user_images.get(user_id)
            # 分類 (classfilter.pyの処理)
            result = predict(image_path)

            # 次のノードへ移り、ボタンを作成
            next_node = Nodes[result["class"]]
            # メッセージとボタン送信
            await interaction.response.send_message(
                f"{result['class']}である確率は…{result['confidence']:.2%}です。\n\n {next_node['message']}",
                ephemeral=True,
            )
        # 次の会話を取得 (id"predict"ではないもの)
        elif next_id in Nodes:
            next_node = Nodes[next_id]
            message_text = next_node["message"]

            # 撮影する際
            # カメラサーバーのリンクを送る
            if next_id == "圧着_カメラ":
                user_id = interaction.user.id
                message_text += f"\n{public_url}?user_id={user_id}"
            # 選択肢がある場合ボタン作成
            if "options" in next_node:
                new_view = ChatbotView(next_node["options"])
                await interaction.response.send_message(
                    message_text, view=new_view, ephemeral=True
                )
            else:
                await interaction.response.send_message(message_text, ephemeral=True)
        # 会話がない時
        else:
            await interaction.response.send_message(
                "すみません。次の会話データが見つかりませんでした。m(_ _)m",
                ephemeral=True,
            )


# メッセージが送信された場合
# チャットボット起動
@bot.event
async def on_message(message):
    # 送信者がボットなら、何もしない
    if message.author.bot:
        return

    # 最初の会話ID"start"を開始
    start_node = Nodes["start"]
    message_text = start_node["message"]

    # 選択肢ボタン作成
    view = ChatbotView(start_node["options"])
    await message.channel.send(f"{bot.user}さん" + message_text, view=view)

    await bot.process_commands(message)


# discord ボット起動 (ターミナル出力)
@bot.event
async def on_ready():
    print(f"{bot.user}さんのところへログインしました")


# Discord Botの起動・接続
bot.run(TOKEN)
