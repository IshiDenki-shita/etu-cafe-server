from datetime import datetime, timezone, timedelta
import os
from dataclasses import dataclass
from flask import Flask, jsonify, request, Response


def require_env(key: str) -> str:
    val = os.getenv(key)
    if val is None:
        raise RuntimeError(f"環境変数 {key} が未定義")
    return val


app = Flask(__name__)


@app.get("/")
def connection_test():
    return jsonify({"matsu_mac alive": True}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
