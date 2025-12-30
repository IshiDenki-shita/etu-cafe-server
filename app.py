"""
松本VPSでやること。
・スマホからのPOSTを受け取る
・受け取った献立表.jsonを ルート/hisotry にセーブする
・斎藤VPSに献立表jsonをPOSTする
"""

from flask import Flask, request, jsonify
import json
from pathlib import Path
from datetime import datetime

# このapp.pyのパス。.resolveで絶対パスにする
path_HERE = Path(__file__).resolve()
# バックアップ用のフォルダ history のパスを格納
path_history = path_HERE.parent  / 'history'

app = Flask(__name__)


# この変数に最新の献立表(json)が入る
latest_menu = {}

# 受け取ったjsonをhistoryフォルダにバックアップ
def save_latest(post_time, latest_menu):
    # 一日ごとに分けてバックアップフォルダを作成
    folder_name = (
        str(post_time.year) + "-" + str(post_time.month) + "-" + str(post_time.day)
    )
    folder_path = path_history / folder_name

    try:
        folder_path.mkdir()
    except Exception as e:
        print(e)
        print(f'{folder_name} フォルダは存在しています。')

    # そのフォルダの中にファイルを作る
    file_name = folder_name + '- ' + str(post_time.hour) + ':' + str(post_time.minute) + ':' + str(post_time.second) + '.json'
    file_path = path_history / folder_name / file_name
    with open(
        file_path,
        'w',
        encoding='utf-8',
    ) as f:
        f.write(json.dumps(latest_menu))


# POSTを貰ってデータを格納する関数
@app.post("/menu_post")
def receive_menu_json():
    latest_menu = request.get_json()

    now = datetime.now()
    save_latest(now, latest_menu)

    return jsonify({"matsu_VPS_received":True}) , 200
