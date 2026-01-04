"""
色々なインポート
"""
from flask import Flask, request, jsonify, Response
import requests
from pathlib import Path
import json
from datetime import datetime


"""
必要なURLや、このファイルからの相対パス設定用
"""
# 斎藤VPS（ラズパイ直上VPS）のURL
url_saitoVPS = "http://127.0.0.1:5001/cafe_menu"

# このapp.pyのパス。.resolveで絶対パスにする
path_HERE = Path(__file__).resolve()
# バックアップ用のフォルダ history のパスを格納。 matsu_vps_cafe/historyにバックアップフォルダ作りたい。
path_history = path_HERE.parent.parent / 'history'
# history 自体が無いと日付フォルダ作成が失敗するので、親を先に作る
path_history.mkdir(parents=True, exist_ok=True)


"""
flaskr.pyを通して使う変数など
"""
# flaskサーバー本体
app = Flask(__name__)

# 松本VMからPOSTされたデータを格納
latest_data_bytes = None


"""
受け取ったjsonをhistoryフォルダにバックアップ
"""
def save_latest(post_time, latest_data):
    # 一日ごとに分けてバックアップフォルダを作成
    folder_name = post_time.strftime("%Y-%m-%d")
    folder_path = path_history / folder_name

    try:
        folder_path.mkdir(exist_ok=True)
    except Exception as e:
        print(e)
        print(f'{folder_name} フォルダを作れませんでした。')

    # そのフォルダの中にファイルを作る
    file_name = f"{folder_name}_{post_time.strftime('%H%M%S')}.json"
    file_path = path_history / folder_name / file_name
    with open(
        file_path,
        'w',
        encoding='utf-8',
    ) as f:
        # 一旦辞書にする
        try:
            latest_dict = json.loads(latest_data)
        except Exception as e:
            print(e)
            
        # その辞書を書式設定しながらjsonに戻す。
        latest_save = json.dumps(latest_dict, ensure_ascii=False, indent=2)
        f.write(latest_save)

"""
postで受け取ったjsonを斎藤VPSにpostする関数
"""
def post_to_saito(latest_data):
    header = {"Content-Type": "application/json"}
    try:
        res = requests.post(url_saitoVPS, data=latest_data, headers=header, timeout=5)
        print("\n齋藤VPSのPOSTに対するレスポンスのステータスコード\n")
        print(res.status_code)
        print("\n齋藤VPSのPOSTに対するレスポンスのテキスト\n")
        print(res.text)
    except requests.exceptions.RequestException as e:
        print("\nあかーん post受け取り失敗")
        print(e)

"""
POSTを貰ってデータを格納する関数
"""
@app.post("/menu_post")
def receive_menu_json():
    # Content-Type がJSONか確認（厳密にしたい場合）
    ct = request.headers.get("Content-Type", "")
    if "application/json" not in ct:
        return (
            jsonify({"ok": False, "error": "Content-Type must be application/json"}),
            415,
        )

    # JSONとしてパース（壊れてたら None）
    parsed = request.get_json(silent=True)
    if parsed is None:
        return jsonify({"ok": False, "error": "Invalid JSON"}), 400

    # postで受け取ったデータをGET待ちにするための箱
    global latest_data_bytes
    latest_data_bytes = request.get_data()

    # historyフォルダ内にバックアップ
    now = datetime.now()
    save_latest(now, latest_data_bytes)
    # 斎藤VPSに転送
    post_to_saito(latest_data_bytes)

    return jsonify({"matsu_VPS_received":True}) , 200

"""
斎藤VPSからのGETリクエストに返信
"""
@app.get("/menu_get")
def send_menu_json():
    # latest_data_bytes is global valuable
    if latest_data_bytes is None:
        return jsonify({"matsu_VPS_has_data": False}), 404
    
    return Response(latest_data_bytes, content_type="application/json")

"""
"""
def main():
    app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    main()
