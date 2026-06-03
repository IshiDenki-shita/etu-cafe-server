import requests
from datetime import datetime, timezone, timedelta

# 松本VPSへのURL
url = "http://133.242.22.254:8081/menu_post/json"
# url = "http://127.0.0.1:8081/menu_post/json"

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
        {
            "generated_at": "2026-06-01T05:12:56Z",
            "menus": [
                {"date": "2026-6-1", "name": "餃子ラーメン", "price": 500},
                {"date": "2026-6-2", "name": "甘辛チキンカツ丼", "price": 500},
                {"date": "2026-6-3", "name": "海鮮丼", "price": 500},
                {"date": "2026-6-4", "name": "胡麻チゲ冷麺", "price": 500},
                {"date": "2026-6-5", "name": "胡麻チゲ冷麺", "price": 500},
                {"date": "2026-6-8", "name": "熊本ラーメン", "price": 500},
                {"date": "2026-6-9", "name": "おろしカツ丼", "price": 500},
                {"date": "2026-6-15", "name": "唐揚げラーメン", "price": 500},
                {"date": "2026-6-17", "name": "ねぎとろ丼", "price": 500},
                {"date": "2026-6-22", "name": "唐揚げ冷麺", "price": 500},
            ],
        }
    ],
}


def post_dammy_menu(url, menu_dict):
    # json= 引数を使うことで、ヘッダに applicaton/json が含まれる
    res = requests.post(url, json=menu_dict)

    print(f"ステータスコード：{res.status_code}")
    print(f"\nレスポンス本文\n{res.text}")


def main():
    print("\nPOSTを投げます\n")
    post_dammy_menu(url, menu_dict)


main()
