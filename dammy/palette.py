""" """

"""
色々なインポート
"""
from flask import Flask, request, jsonify
import requests
from pathlib import Path
import json
from datetime import datetime
import time

app = Flask(__file__)

"""
必要なURLや、このファイルからの相対パス設定用
"""
# 斎藤VPS（ラズパイ直上VPS）のURL
url_saitoVPS = "http://127.0.0.1:5000"


"""
postで受け取ったjsonを斎藤VPSにpostする関数
"""
def post_to_saito(latest_menu):
    try:
        res = requests.post(url_saitoVPS, json=latest_menu)
    except Exception as e:
        print("\nあかーん エラー発生")
        print(e)
        
menu_dict = {
    "generated_at": "2025-12-30T23:19:51+09:00",
    "menus": [
        {"name": "担々麺", "price": 200, "date": "2026-01-20", "price": 500},
        {"name": "春巻き", "price": 300, "date": "2026-01-21", "price": 130},
    ]
}

menu = json.dumps(menu_dict, ensure_ascii=False)

print("\n\n作られたjson")
print(menu)
post_to_saito(menu)
