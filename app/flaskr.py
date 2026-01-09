"""
色々なインポート
"""
from flask import Flask, request, jsonify, Response
import requests
from pathlib import Path
import json
from datetime import datetime, timezone, timedelta


"""
必要なURLや、このファイルからの相対パス設定用
"""
# 斎藤VPS（ラズパイと通信するVPS）のURL
url_saitoVPS = "http://162.43.43.163:8080/cafe"
# url_saitoVPS = "http://127.0.0.1:5001/cafe/menu" 

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
            return False

        # その辞書を書式設定しながらjsonに戻す。
        latest_save = json.dumps(latest_dict, ensure_ascii=False, indent=2)
        f.write(latest_save)
    
    return True

"""
post/被getするときに使う、最新のバックアップを探す関数
"""
def _find_latest_backup_file():
    """
    history配下から「最新のバックアップjson」を探して返す。
    ルール:
      - 日付フォルダ（YYYY-MM-DD）を新しい順に見る
      - その中の *.json を更新時刻(newest)順に見て最初の1件
    """
    if not path_history.exists():
        # 流石にそんなことはないやろ
        return None

    day_dirs = sorted(
        [p for p in path_history.iterdir() if p.is_dir()],
        key=lambda p: p.name,  # YYYY-MM-DD の文字列ソートで時系列になる
        reverse=True,
    )

    for d in day_dirs:
        files = sorted(
            [p for p in d.glob("*.json") if p.is_file()],
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if files:
            return files[0]
    return None


"""
最新バックアップを斎藤VPSにpostする関数
"""
def post_to_saito():
    # バックアップ内の最新のjsonを斎藤VPSへpostする
    latest_file = _find_latest_backup_file()
    if latest_file is None:
        print("あかーん: history にバックアップが1件も無いので送れない")
        return False

    try:
        payload_text = latest_file.read_text(encoding="utf-8")
    except Exception as e:
        print("あかーん: 最新バックアップの読み込み失敗")
        print(e)
        return False

    header = {"Content-Type": "application/json"}
    try:
        res = requests.post(
            url_saitoVPS, data=payload_text.encode("utf-8"), headers=header, timeout=5
        )
        print("\n齋藤VPSのPOSTに対するレスポンスのステータスコード\n")
        print(res.status_code)
        print("\n齋藤VPSのPOSTに対するレスポンスのテキスト\n")
        print(res.text)
    except requests.exceptions.RequestException as e:
        print("\nあかーん 斎藤VPSへのpost失敗")
        print(e)
        return False
    
    return True

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
        return jsonify({"matsu_vps_ok": False, "error": "Invalid JSON"}), 400

    # postで受け取ったデータをGET待ちにするための箱
    global latest_data_bytes
    latest_data_bytes = request.get_data()

    # historyフォルダ内にバックアップ
    now = datetime.now(timezone(timedelta(hours=9)))
    if not save_latest(now, latest_data_bytes):
        return jsonify({"matsu_vps_ok":False, "error":"not saved"})
    
    # 最新のバックアップを斎藤VPSに転送
    posted = post_to_saito()
    if not posted:
        return jsonify({"matsu_VPS_received":False,"error":"post to saito failed"})

    return jsonify({"matsu_VPS_received":True}) , 200

"""
斎藤VPSからのGETリクエストに返信（最新バックアップを返す）
"""
@app.get("/menu_get")
def send_menu_json():
    # 最新バックアップのパス
    latest_file = _find_latest_backup_file()
    if latest_file is None:
        return jsonify({"matsu_VPS_has_data": False, "error": "no backup yet"}), 404

    try:
        payload_text = latest_file.read_text(encoding="utf-8")
    except Exception as e:
        print("あかーん: 最新バックアップの読み込み失敗")
        print(e)
        return jsonify({"matsu_VPS_has_data": False, "error": "read backup failed"}), 500

    # 念のためJSONとして妥当かチェック（壊れてたら500）
    try:
        json.loads(payload_text)
    except Exception as e:
        print("あかーん: 最新バックアップが壊れてる/JSONではない")
        print(e)
        return jsonify({"matsu_VPS_has_data": False, "error": "invalid json"}), 500

    # そのままJSONとして返す
    print("\nGETされました。")
    return Response(payload_text, content_type="application/json; charset=utf-8")


"""
メイン関数
"""
def main():
    app.run(host="::", port=8080)

"""
メイン関数実行
"""
if __name__ == "__main__":
    main()
