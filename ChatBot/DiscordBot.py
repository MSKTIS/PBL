import json
import threading
import time

import discord
from discord.ext import commands
from flask import Flask, render_template
from pyngrok import ngrok

# カメラサーバー
cameraSever = Flask(__name__)


@cameraSever.route("/")
def index():
    return render_template("WebCamera/camera.html")


def run_flask():
    cameraSever.run(host="0.0.0.0", port=5000)


# flaskを接続 ( 並列処理 )
threading.Thread(target=run_flask, daemon=True).start()
# Flaskの起動待ち
time.sleep(1)

# ngrokでグローバルなurl作成
public_url = ngrok.connect(5000).public_url
print(f"URL: {public_url}")

# discord ボット
# Botのリンク見たいなもん
# 本番ではDiscord Botのトークンを入れよう
TOKEN = "KoreHaNisemonoNoToken"

# Botに読み取り権限を付与する
intents = discord.Intents.default()
intents.message_content = True

# discordボット作成
bot = commands.Bot(command_prefix="!", intents=intents)

# JSON形式の会話データを読み込み
with open("chatbot.json", "r", encoding="utf-8") as f:
    chatbot_data = json.load(f)
# id別の会話データ
Nodes = {node["id"]: node for node in chatbot_data["chat"]}


# discord ボタン機能
class ChatbotView(discord.ui.View):
    # 初期化
    def __init__(self, options):
        super().__init__(timeout=None)
        # id別にボタンを作る
        for option in options:
            button = discord.ui.Button(
                label=option["text"],
                custom_id=option.get("next_id"),
            )
            # ボタンが押されたときの処理
            button.callback = self.button_callback
            self.add_item(button)

    # ボタンが押されたときの処理
    async def button_callback(self, interaction: discord.Interaction):
        # 押されたボタンのidを取得
        next_id = interaction.data["custom_id"]

        # 次の会話を取得
        if next_id in Nodes:
            next_node = Nodes[next_id]
            message_text = next_node["message"]

            # 次の選択肢ボタンを作成
            if "options" in next_node:
                new_view = ChatbotView(next_node["options"])
                await interaction.response.send_message(
                    message_text, view=new_view, ephemeral=True
                )
            # 選択肢がない場合
            else:
                # カメラ撮影のURL
                if next_id == "camera":
                    message_text += f"\n{public_url}"
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
    await message.channel.send(f"{bot.user}さん" + message_text)

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
