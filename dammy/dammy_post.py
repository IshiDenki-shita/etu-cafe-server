import requests
import json

# 松本VPSへのURL
url = "http://100.122.164.48:5000/menu_post"

menu_dict = {
    "menu1": {"name": "担々麺", "date": '2026-1-20'},
    "menu2": {"name": "春巻き", "date": '2026-1-21'},
}


def post_dammy_menu(url, menu_dict):
    dammy_json = json.dumps(menu_dict)
    # json= 引数を使うことで、ヘッダに applicaton/json が含まれる
    res = requests.post(url, json=menu_dict)

    print("\nステータスコード\n")
    print(res.status_code)

    print("\nレスポンス本文\n")
    print(res.text)


def main():
    print("\nPOSTを投げます\n")

    post_dammy_menu(url, menu_dict)

main()
