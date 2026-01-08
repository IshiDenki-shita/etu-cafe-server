import requests
from datetime import datetime, timezone, timedelta

# 松本VPSへのURL
url = "http://100.122.164.48:5000/menu_post"
# url = "http://127.0.0.1:5000/menu_post"

# JST(+09:00)のISO8601文字列を生成（例: 2026-01-05T12:34:56+09:00）
JST = timezone(timedelta(hours=9))

menu_dict = {
    "generated_at": datetime.now(JST).isoformat(timespec="seconds"),
    "menus": [
        {"name": "ダミー担々麺", "date": "2026-01-20", "price": 500},
        {"name": "ダミー春巻き", "date": "2026-01-21", "price": 130},
        {"name": "ダミー親子丼", "date": "2026-01-22", "price": 550}
    ],
}


def post_dammy_menu(url, menu_dict):
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
