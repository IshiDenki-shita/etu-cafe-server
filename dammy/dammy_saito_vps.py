# 偽の斎藤VPS

from flask import Flask, request, jsonify
import requests
import json

app = Flask(__file__)


@app.post("/")
def receive_menu_json():
    latest_data = request.get_data()
    latest_dict = json.loads(latest_data)

    print("\n受け取ったJSONを辞書に開封")
    print(latest_dict)

    return jsonify({"matsu_VPS_received": True}), 200
