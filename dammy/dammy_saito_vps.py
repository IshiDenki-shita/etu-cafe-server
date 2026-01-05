# 偽の斎藤VPS

from flask import Flask, request, jsonify
import json

app = Flask(__file__)


@app.post("/cafe/menu")
def receive_menu_json():
    latest_data = request.get_data()
    latest_dict = json.loads(latest_data)

    print("\n受け取ったJSONを辞書に開封")
    print(latest_dict)

    return jsonify({"matsu_VPS_received": True}), 200

def main():
    app.run(host="127.0.0.1", port=5001)

main()