import os

from flask import Flask, send_from_directory

# カレントディレクトリ（今いるフォルダ）をルートとしてファイルを配信する設定
app = Flask(__name__, static_folder=".", static_url_path="")


@app.route("/")
def index():
    # index.html を返す
    return send_from_directory(".", "index.html")


if __name__ == "__main__":
    # host='0.0.0.0' でスマホからのアクセスを許可
    # ssl_context='adhoc' で自動的にHTTPS化
    app.run(host="0.0.0.0", port=8000, debug=True, ssl_context="adhoc")
