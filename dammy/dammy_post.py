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
        {"name": "担々麺", "date": "2026-05-1", "price": 500},
        {"name": "餃子ラーメン", "date": "2026-05-7", "price": 500},
        {"name": "熊本ラーメン", "date": "2026-05-11", "price": 500},
        {"name": "温玉サーモン丼", "date": "2026-05-12", "price": 500},
        {"name": "ブリとろろ丼", "date": "2026-05-13", "price": 500},
        {"name": "熊本ラーメン", "date": "2026-05-15", "price": 500},
        {"name": "タコライス", "date": "2026-05-19", "price": 500},
        {"name": "豚塩カルビ丼", "date": "2026-05-20", "price": 500},
        {"name": "柚子胡椒香る！鶏塩まぜそば", "date": "2026-05-21", "price": 500},
        {"name": "柚子胡椒香る！鶏塩まぜそば", "date": "2026-05-22", "price": 500},
        {"name": "唐揚げラーメン", "date": "2026-05-25", "price": 500},
        {"name": "熊本ラーメン", "date": "2026-05-28", "price": 500},
        {"name": "柚子胡椒香る！鶏塩まぜそば", "date": "2026-05-29", "price": 500},
        {"name": "カツ玉丼", "date": "2026-05-1", "price": 500},
        {"name": "ビビンバ丼", "date": "2026-05-1", "price": 500},
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
