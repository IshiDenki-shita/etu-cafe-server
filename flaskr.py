"""
色々なインポート
"""
from flask import Flask, request, jsonify
import requests
from pathlib import Path
import json
from datetime import datetime


"""
必要なURLや、このファイルからの相対パス設定用
"""
# 斎藤VPS（ラズパイ直上VPS）のURL
url_saitoVPS = "http://127.0.0.1:5001"

# このapp.pyのパス。.resolveで絶対パスにする
path_HERE = Path(__file__).resolve()
# バックアップ用のフォルダ history のパスを格納
path_history = path_HERE.parent  / 'history'
# history 自体が無いと日付フォルダ作成が失敗するので、親を先に作る
path_history.mkdir(parents=True, exist_ok=True)


"""
flaskr.pyを通して使う変数など
"""
app = Flask(__name__)


"""
受け取ったjsonをhistoryフォルダにバックアップ
"""
def save_latest(post_time, latest_data):
    # 一日ごとに分けてバックアップフォルダを作成
    folder_name = (
        str(post_time.year) + "-" + str(post_time.month) + "-" + str(post_time.day)
    )
    folder_path = path_history / folder_name

    try:
        folder_path.mkdir(exist_ok=True)
    except Exception as e:
        print(e)
        print(f'{folder_name} フォルダは存在しています。')

    # そのフォルダの中にファイルを作る
    file_name = f"{folder_name}_{post_time.strftime('%H%M%S')}.json"
    file_path = path_history / folder_name / file_name
    with open(
        file_path,
        'w',
        encoding='utf-8',
    ) as f:
        # 一旦辞書にする
        latest_dict = json.loads(latest_data)
        latest_save = json.dumps(latest_dict, ensure_ascii=False, indent=2)
        f.write(latest_save)

"""
postで受け取ったjsonを斎藤VPSにpostする関数
"""
def post_to_saito(latest_data):
    header = {"Content-Type": "application/json"}
    try:
        res = requests.post(url_saitoVPS, data=latest_data, headers=header, timeout=5)
    except Exception as e:
        print("\nあかーん post受け取り失敗")
        print(e)

"""
POSTを貰ってデータを格納する関数
"""
@app.post("/menu_post")
def receive_menu_json():
    latest_data = request.get_data()

    now = datetime.now()
    # historyフォルダ内にバックアップ
    save_latest(now, latest_data)
    # 斎藤VPSに転送
    post_to_saito(latest_data)

    return jsonify({"matsu_VPS_received":True}) , 200
