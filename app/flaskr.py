"""
色々なインポート
"""

from datetime import datetime, timezone, timedelta
import json
from pathlib import Path
import requests
import os
import sys
from dataclasses import dataclass
from dotenv import load_dotenv
from flask import Flask, request, jsonify, Response


@dataclass
class Config_env:
    def __init__(self):
        """
        環境変数読み込み
        """
        load_dotenv()
        self.app = Flask(__name__)

        # --- アプリ設定 ---
        self.ENV = os.getenv("FLASK_ENV", "development")
        self.DEBUG = os.getenv("DEBUG", "False") == "True"
        self.HOST = os.getenv("HOST", "0.0.0.0")
        self.PORT = int(os.getenv("PORT", 5000))
        self.BASE_URL = os.getenv("APP_URL")

        # 送受信用
        self.PHONE_AUTH_TOKEN = os.getenv("PHONE_AUTH_TOKEN")  # スマホの認証
        self.SAITO_VPS_URL = os.getenv("SAITO_VPS_URL")  # 斎藤VMへのURL
        assert self.SAITO_VPS_URL is not None

        # 保存用
        self.PHOTOS_DIR = os.getenv("PHOTOS_DIR", "/tmp")  # 画像保存先
        self.HISTORY_DIR = os.getenv("HISTORY_DIR")
        assert self.HISTORY_DIR is not None


app = Flask(__name__)
cfg = Config_env()

latest_data_bytes = None
history_dir = Path(cfg.HISTORY_DIR)
history_dir.mkdir(parents=True, exist_ok=True)


def save_latest(post_time, latest_data):
    # 一日ごとに分けてバックアップフォルダを作成
    folder_name = post_time.strftime("%Y-%m-%d")
    folder_path = history_dir / folder_name

    try:
        folder_path.mkdir(exist_ok=True)
    except Exception as e:
        print(e)
        print(f"{folder_name} フォルダを作れませんでした。")

    # そのフォルダの中にファイルを作る
    file_name = f"{folder_name}_{post_time.strftime('%H%M%S')}.json"
    file_path = history_dir / folder_name / file_name
    with open(
        file_path,
        "w",
        encoding="utf-8",
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


def _find_latest_backup_file():
    """
    history配下から「最新のバックアップjson」を探して返す。
    ルール:
      - 日付フォルダ（YYYY-MM-DD）を新しい順に見る
      - その中の *.json を更新時刻(newest)順に見て最初の1件
    """

    day_dirs = sorted(
        [p for p in history_dir.iterdir() if p.is_dir()],
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
        if cfg.SAITO_VPS_URL is not None:
            res = requests.post(
                cfg.SAITO_VPS_URL,
                data=payload_text.encode("utf-8"),
                headers=header,
                timeout=5,
            )
        else:
            print(f"斎藤VPSのURLに問題あり")
            return False
        print("\n齋藤VPSのPOSTに対するレスポンスのステータスコード\n")
        print(res.status_code)
        print("\n齋藤VPSのPOSTに対するレスポンスのテキスト\n")
        print(res.text)
    except requests.exceptions.RequestException as e:
        print("\nあかーん 斎藤VPSへのpost失敗")
        print(e)
        return False

    if not res.ok:  # 200-399以外
        print("\nあかーん: 斎藤VPSがエラーを返した")
        print(res.status_code)
        print(res.text)
        return False

    return True


@app.post("/menu_post")
def receive_menu_json():
    # Content-Type がJSONか確認（厳密にしたい場合）
    ct = request.headers.get("Content-Type", "")
    if "application/json" not in ct:
        return (
            jsonify(
                {
                    "matsu_vps_received": False,
                    "error": "Content-Type must be application/json",
                }
            ),
            415,
        )

    # JSONとしてパース（壊れてたら None）
    parsed = request.get_json(silent=True)
    if parsed is None:
        return jsonify({"matsu_vps_received": False, "error": "Invalid JSON"}), 400

    # postで受け取ったデータをGET待ちにするための箱
    global latest_data_bytes
    latest_data_bytes = request.get_data()

    # historyフォルダ内にバックアップ
    now = datetime.now(timezone(timedelta(hours=9)))
    if not save_latest(now, latest_data_bytes):
        return jsonify({"matsu_vps_received": False, "error": "not saved"})

    # 最新のバックアップを斎藤VPSに転送
    posted = post_to_saito()
    if not posted:
        return (
            jsonify({"matsu_vps_received": True, "error": "post to saito failed"}),
            400,
        )

    return jsonify({"matsu_VPS_received": True, "error": "No error"}), 200


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
        return (
            jsonify({"matsu_VPS_has_data": False, "error": "read backup failed"}),
            500,
        )

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
if __name__ == "__main__":
    app.run(host=cfg.HOST, port=cfg.PORT, debug=cfg.DEBUG)
