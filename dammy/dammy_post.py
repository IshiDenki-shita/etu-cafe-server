import requests
from datetime import datetime, timezone, timedelta

# 松本VPSへのURL
url = "http://100.90.40.123:8080/menu_post"
# url = "http://127.0.0.1:8080/menu_post"

# JST(+09:00)のISO8601文字列を生成（例: 2026-01-05T12:34:56+09:00）
JST = timezone(timedelta(hours=9))

# 斎藤VPSに送るJSONのgenerated_atの日付のフォーマットを固定する。
def now_jst_iso8601_seconds() -> str:
    """
    斎藤VPS指定フォーマット:
    2024-12-02T14:30:00+09:00
    """
    dt = datetime.now(JST).replace(microsecond=0)  # 秒までに丸める
    s = dt.isoformat()  # 'YYYY-MM-DDTHH:MM:SS+09:00'
    # 念のためオフセットが +0900 のようになったケースを +09:00 に補正
    if len(s) >= 5 and (s[-5] in ["+", "-"]) and s[-3] != ":":
        s = s[:-2] + ":" + s[-2:]
    return s


menu_dict = {
    "generated_at": now_jst_iso8601_seconds(),
    "menus": [
        {"name": "ダミー斎藤手作りおにぎり", "date": "2026-01-19", "price": 500},
        {"name": "塩だれカツ丼", "date": "2026-01-7", "price": 0},
        {"name": "唐揚げラーメン", "date": "2026-01-7", "price": 0},
        {"name": "餃子ラーメン", "date": "2026-01-13", "price": 0},
        {"name": "唐揚げ麻婆丼", "date": "2026-01-13", "price": 0},
        {"name": "ピリ辛サーモン丼", "date": "2026-01-14", "price": 0},
        {"name": "ちく天うどん・そば", "date": "2026-01-15", "price": 0},
        {"name": "海老天うどん", "date": "2026-01-16", "price": 0},
        {"name": "蒸し鶏ごま味噌ラーメン", "date": "2026-01-19", "price": 0},
        {"name": "炭火焼鳥丼", "date": "2026-01-20", "price": 0},
        {"name": "和風カツ丼", "date": "2026-01-21", "price": 0},
        {"name": "そぼろあんかけうどん・そば", "date": "2026-01-22", "price": 0},
        {"name": "そぼろあんかけうどん・そば", "date": "2026-01-22", "price": 0},
        {"name": "唐揚げラーメン", "date": "2026-01-26", "price": 0},
        {"name": "ピリ辛ネギトロ丼", "date": "2026-01-27", "price": 0},
        {"name": "豚塩カルビ丼", "date": "2026-01-28", "price": 0},
        {"name": "とり天うどん・そば", "date": "2026-01-29", "price": 0},
        {"name": "とり天うどん・そば", "date": "2026-01-30", "price": 0},
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
