# 偽の斎藤VPS

from flask import Flask, request, jsonify
import json

app = Flask(__file__)

"""
松本VMからのPOSTリクエストを受ける機能
"""
@app.post("/cafe/menu")
def receive_menu_json():
    latest_data = request.get_data()
    latest_dict = json.loads(latest_data)

    print("\n受け取ったJSONを辞書に開封")
    print(latest_dict)

    return jsonify({"matsu_VPS_received": True}), 200

"""
ラズパイからのGETリクエストを受ける機能
"""
dammy_dict = {
    "timetable": {},
    "train": {},
    "cafe": {
        "menus":[
            {"name":"ダミーうどん", "date":"2026-01-08", "price":"500"}
        ]
    }
}

@app.get("/rasp_get")
def send_to_rasp():
    print("\n\nラズパイからGETリクエストが来ました。\n")
    return jsonify(dammy_dict)


def main():
    app.run(host="127.0.0.1", debug=True, port=5001)

main()