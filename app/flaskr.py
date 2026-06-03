from datetime import datetime, timezone, timedelta
import json
from pathlib import Path
import requests
import os
from dataclasses import dataclass
import threading
from dotenv import load_dotenv
from flask import Flask, jsonify, request, Response
import subprocess
import re


def require_env(key: str) -> str:
    val = os.getenv(key)
    if val is None:
        raise RuntimeError(f"環境変数 {key} が未定義")
    return val


@dataclass(frozen=True)
class Config_env:
    ENV: str
    DEBUG: bool
    HOST: str
    PORT: int
    APP_URL: str
    PHONE_AUTH_TOKEN: str
    SAITO_VPS_URL: str
    HISTORY_DIR: str
    PHOTOS_DIR: str

    @staticmethod
    def load() -> "Config_env":

        load_dotenv()

        return Config_env(
            ENV=os.getenv("FLASK_ENV", "development"),
            DEBUG=os.getenv("DEBUG", "False") == "True",
            HOST=os.getenv("HOST", "0.0.0.0"),
            PORT=int(os.getenv("PORT", "8081")),
            APP_URL=require_env("APP_URL"),
            PHONE_AUTH_TOKEN=require_env("PHONE_AUTH_TOKEN"),
            SAITO_VPS_URL=require_env("SAITO_VPS_URL"),
            HISTORY_DIR=require_env("HISTORY_DIR"),
            PHOTOS_DIR=os.getenv("PHOTOS_DIR", "/"),
        )


cfg = Config_env.load()
app = Flask(__name__)

history_dir = Path(cfg.HISTORY_DIR)
history_dir.mkdir(parents=True, exist_ok=True)

latest_data_bytes: bytes | None = None
data_lock = threading.Lock()


def save_latest(post_time: datetime, latest_data: bytes) -> bool:
    folder_name = post_time.strftime("%Y-%m-%d")
    folder_path = history_dir / folder_name

    folder_path.mkdir(exist_ok=True)

    file_name = f"{folder_name}_{post_time.strftime('%H%M%S')}.json"
    file_path = folder_path / file_name

    try:
        latest_dict = json.loads(latest_data)
    except Exception as e:
        print(f"セーブ時にJSONを読み込めませんでした。\n{e}")
        return False

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(latest_dict, f, ensure_ascii=False, indent=2)

    return True


def find_latest_backup_file():
    day_dirs = sorted(
        [p for p in history_dir.iterdir() if p.is_dir()],
        key=lambda p: p.name,
        reverse=True,
    )

    for d in day_dirs:
        files = sorted(
            d.glob("*.json"),
            key=lambda p: p.name,
            reverse=True,
        )
        if files:
            return files[0]

    return None


def post_to_saito() -> bool:
    latest_file = find_latest_backup_file()
    if latest_file is None:
        print(f"斎藤VPSの送信時に最新バックアップを取得できませんでした。")
        return False

    try:
        payload_text = latest_file.read_text(encoding="utf-8")
    except Exception as e:
        print(f"最新バックアップのJSONを読めませんでした\n{e}")
        return False

    url = cfg.SAITO_VPS_URL

    try:
        res = requests.post(
            url,
            data=payload_text.encode("utf-8"),
            headers={"Content-Type": "application/json"},
            timeout=5,
        )

    except requests.RequestException:
        return False

    return res.ok


@app.post("/menu_post/json")
def receive_menu_json():
    if "application/json" not in request.headers.get("Content-Type", ""):
        return jsonify({"error": "Content-Type must be application/json"}), 415

    parsed = request.get_json(silent=True)
    if parsed is None:
        return jsonify({"error": "Invalid JSON"}), 400

    with data_lock:
        global latest_data_bytes
        latest_data_bytes = request.get_data()

    now = datetime.now(timezone(timedelta(hours=9)))

    if latest_data_bytes is None or not save_latest(now, latest_data=latest_data_bytes):
        return jsonify({"matsu_vps_alive": "true", "error": "save failed"}), 500

    if not post_to_saito():
        return (
            jsonify(
                {"matsu_vps_alive": "true", "error": "post to saito server failed"}
            ),
            500,
        )

    return jsonify({"ok": True}), 200


@app.post("/menu_post/photo")
def receive_menu_img():
    # トークン認証
    token = request.headers.get("Auth-Token")
    if token != cfg.PHONE_AUTH_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401

    # Content-Typeがmultipart/form-dataであるか確認
    if request.mimetype != "multipart/form-data":
        return (
            jsonify({"error": "Unsupported Media Type. Expected multipart/form-data"}),
            415,
        )

    # リクエストファイルの存在確認
    if not request.files:
        return jsonify({"error": "No file provided"}), 400

    file = next(iter(request.files.values()))

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    filename = file.filename

    # ファイル名形式の検証 (例: don-20260529180000.jpeg)
    pattern = r"^(don|men)-\d{14}\.(jpg|jpeg)$"
    if not re.match(pattern, filename, flags=re.IGNORECASE):
        return (
            jsonify(
                {
                    "error": "Invalid filename format. Expected don- or men-yyyyMMddHHmmss.jpg or .jpeg"
                }
            ),
            400,
        )

    # 拡張子の統一とプレフィックスの抽出
    base_name = filename.rsplit(".", 1)[0]
    new_filename = f"{base_name}.jpeg"
    prefix = base_name.split("-")[0]

    # 保存先ディレクトリの決定 (catched/YYYY-MM) と作成
    jst = timezone(timedelta(hours=9))
    now = datetime.now(jst)
    month_str = now.strftime("%Y-%m")
    save_dir = Path(cfg.PHOTOS_DIR) / "catched" / month_str
    save_dir.mkdir(parents=True, exist_ok=True)

    # 同一プレフィックスの古いファイルを削除
    for existing_file in save_dir.glob(f"{prefix}-*.jpeg"):
        try:
            existing_file.unlink()
        except OSError as e:
            return jsonify({"error": f"Failed to delete old file: {e}"}), 500

    # ファイルの保存
    save_path = save_dir / new_filename
    file.save(str(save_path))

    return (
        jsonify({"message": "File saved successfully", "saved_path": str(save_path)}),
        200,
    )


@app.get("/menu_get")
def send_menu_json():
    latest_file = find_latest_backup_file()
    if latest_file is None:
        print(f"斎藤VPSからのGET時に最新バックアップを取得できませんでした。")
        return jsonify({"matsu_vps_alive": "true", "error": "no data"}), 404

    try:
        payload_text = latest_file.read_text(encoding="utf-8")
        json.loads(payload_text)
    except Exception as e:
        print(f"被GET時にJSONがおかしい")
        return jsonify({"matsu_vps_alive": "true", "error": "invalid data"}), 500

    return Response(payload_text, content_type="application/json")


if __name__ == "__main__":
    app.run(host=cfg.HOST, port=cfg.PORT, debug=cfg.DEBUG)
