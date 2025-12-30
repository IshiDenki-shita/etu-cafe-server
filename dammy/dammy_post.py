import requests
import json

# 松本VPSへのURL
url = "http://127.0.0.1:5000/menu_post"

menu_dict = {
    "menu1": {"name": "担々麺", "price": 200, "date": '2026-1-20'},
    "menu2": {"name": "春巻き", "price": 300, "date": '2026-1-21'},
}


def post_dammy_menu(url, menu_dict):
    dammy_json = json.dumps(menu_dict)
    res = requests.post(url, json=menu_dict)

    print("\nステータスコード\n")
    print(res.status_code)

    print("\nレスポンス本文\n")
    print(res.text)


def main():
    print("\nPOSTを投げます\n")

    post_dammy_menu(url, menu_dict)

main()