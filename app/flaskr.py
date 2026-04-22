from datetime import datetime, timezone, timedelta
import json
from pathlib import Path
import requests
import os
from dataclasses import dataclass
from dotenv import load_dotenv
from flask import Flask, request, jsonify, Response


# =========================
# 環境変数ユーティリティ
# =========================
def require_env(key: str) -> str:
    val = os.getenv(key)
    if val is None:
        raise RuntimeError(f"環境変数 {key} が未設定")
    return val


# =========================
# 設定クラス
# =========================
@dataclass(frozen=True)
class Config:
    ENV: str
    DEBUG: bool
    HOST: str
    PORT: int
    BASE_URL: str
    PHONE_AUTH_TOKEN: str
    SAITO_VPS_URL: str
    HISTORY_DIR: str
    PHOTOS_DIR: str

    @staticmethod
    def load() -> "Config":
        load_dotenv()

        return Config(
            ENV=os.getenv("FLASK_ENV", "development"),
            DEBUG=os.getenv("DEBUG", "False") == "True",
            HOST=os.getenv("HOST", "0.0.0.0"),
            PORT=int(os.getenv("PORT", "5000")),
            BASE_URL=require_env("APP_URL"),
            PHONE_AUTH_TOKEN=require_env("PHONE_AUTH_TOKEN"),
            SAITO_VPS_URL=require_env("SAITO_VPS_URL"),
            HISTORY_DIR=require_env("HISTORY_DIR"),
            PHOTOS_DIR=os.getenv("PHOTOS_DIR", "/tmp"),
        )


# =========================
# 初期化
# =========================
cfg = Config.load()
app = Flask(__name__)

history_dir = Path(cfg.HISTORY_DIR)
history_dir.mkdir(parents=True, exist_ok=True)

latest_data_bytes: bytes | None = None


# =========================
# 保存処理
# =========================
def save_latest(post_time: datetime, latest_data: bytes) -> bool:
    folder_name = post_time.strftime("%Y-%m-%d")
    folder_path = history_dir / folder_name

    folder_path.mkdir(exist_ok=True)

    file_name = f"{folder_name}_{post_time.strftime('%H%M%S')}.json"
    file_path = folder_path / file_name

    try:
        latest_dict = json.loads(latest_data)
    except Exception:
        return False

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(latest_dict, f, ensure_ascii=False, indent=2)

    return True


# =========================
# 最新ファイル取得
# =========================
def _find_latest_backup_file():
    day_dirs = sorted(
        [p for p in history_dir.iterdir() if p.is_dir()],
        key=lambda p: p.name,
        reverse=True,
    )

    for d in day_dirs:
        files = sorted(
            d.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if files:
            return files[0]

    return None


# =========================
# VPS送信
# =========================
def post_to_saito() -> bool:
    latest_file = _find_latest_backup_file()
    if latest_file is None:
        return False

    try:
        payload_text = latest_file.read_text(encoding="utf-8")
    except Exception:
        return False

    url = cfg.SAITO_VPS_URL  # ← 型は確定str

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


# =========================
# POST API
# =========================
@app.post("/menu_post")
def receive_menu_json():
    if "application/json" not in request.headers.get("Content-Type", ""):
        return jsonify({"error": "Content-Type must be application/json"}), 415

    parsed = request.get_json(silent=True)
    if parsed is None:
        return jsonify({"error": "Invalid JSON"}), 400

    global latest_data_bytes
    latest_data_bytes = request.get_data()

    now = datetime.now(timezone(timedelta(hours=9)))

    if latest_data_bytes is None or not save_latest(now, latest_data_bytes):
        return jsonify({"error": "save failed"}), 500

    if not post_to_saito():
        return jsonify({"error": "post failed"}), 500

    return jsonify({"ok": True}), 200


# =========================
# GET API
# =========================
@app.get("/menu_get")
def send_menu_json():
    latest_file = _find_latest_backup_file()
    if latest_file is None:
        return jsonify({"error": "no data"}), 404

    try:
        payload_text = latest_file.read_text(encoding="utf-8")
        json.loads(payload_text)
    except Exception:
        return jsonify({"error": "invalid data"}), 500

    return Response(payload_text, content_type="application/json")


# =========================
# 起動
# =========================
if __name__ == "__main__":
    app.run(host=cfg.HOST, port=cfg.PORT, debug=cfg.DEBUG)
