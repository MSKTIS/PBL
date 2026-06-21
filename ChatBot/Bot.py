import threading

import discord
from discord.ext import commands
from flask import Flask, render_template

# Botのリンク見たいなもん
TOKEN = "MTUwNjE0NzE0ODY3MDk2MzgzMw.GM2nkN.dtE11qD243WcEMYcx16H-kd07KD5z-HXZ_bi48"

# Botに読み取り権限を付与する
intents = discord.Intents.default()
intents.message_content = True

# ボット
bot = commands.Bot(command_prefix="!", intents=intents)
# サーバー
cameraSever = Flask(__name__)


# カメラサーバー
@cameraSever.route("/")
def index():
    return render_template("camera/camera.html")


def run_flask():
    cameraSever.run(host="0.0.0.0", port=5000)


# Discord Bot
# テスト
@bot.event
async def on_ready():
    print(f"{bot.user} こんにちわ。アシスタントBot")


# テスト
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    print(message.content)

    if message.content == "こんにちは":
        await message.channel.send("こんにちは！")
    await bot.process_commands(message)


# カメラサーバー
@bot.command()
async def camera(ctx):
    await ctx.send("リンクを押して撮影をしてください。\n")
    await ctx.send("https://example.com")


# 並列処理
threading.Thread(target=run_flask).start()

# Discord Botの起動・接続
bot.run(TOKEN)
