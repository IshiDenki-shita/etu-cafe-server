# ラズパイの中で動作するflaskサーバー。GETリクエストも行う

"""
色々なインポート
"""
import time
from dataclasses import dataclass
import requests
from flask import Flask, render_template  # Flaskとテンプレート描画用の render_template をインポート
import threading

"""
色々なグローバル変数
"""
# GETしに行く齋藤VPSのURL
url_saitoVPS = "http://162.43.43.163:8080/board" # URLの階層構造は未定

# html_url
html_url_1 = "page1.html"
html_url_2 = "page2.html"
html_url_3 = "page3.html" # 食堂の特別メニューを表示

# Flaskアプリケーションのインスタンスを作成
app = Flask(__name__)


"""
20秒に一回齋藤VPSにGETリクエスト送る
担当：松本
"""
@dataclass
class data_GET():
    timetable: dict
    train: dict
    cafe: dict
data = data_GET({},{},{})
data_lock = threading.Lock() # これで値の使用中に値を変更できなくなる


"""
齋藤VPSにGETし続ける関数（ゆくゆくはタイムスケジュールで）
"""
def fetch_loop():
    # 真っ当なやり方思いつかんだ
    while True:
        time.sleep(20)

        try:
            r = requests.get(url_saitoVPS ,timeout=5)
            r.raise_for_status()
            data_dict = r.json() # JSONがdictになる
            print("\n\nサーバーへのアクセス成功!!\n\n")

        except requests.RequestException as e:
            print("\n\nあかーん_リクエストでエラー発生!!!!!!!!!!\n\n")
            print(e)
            continue
        except ValueError as e:
            print("\n\nあかーん_GETしたJSONがおかしい!!!!!!!!!!\n\n")
            print(e)
            continue

        with data_lock:
            data.timetable = data_dict.get("timetable", {})
            data.train = data_dict.get("train", {})
            data.cafe = data_dict.get("cafe", {})

"""
main関数
"""
def main():
    t = threading.Thread(target=fetch_loop, daemon=True) # 別スレッドでGETリクエストのループ
    t.start()
    app.run(host="127.0.0.1", debug=True, port=8080)

"""
ChromiumにHTMLを供給する
"""
# 担当：小原
@app.route("/")
def page1():
    return render_template(html_url_1)


# 担当：中田と齋藤
@app.route("/page2")
def page2():
    return render_template(html_url_2)


# 担当：松本
@app.route("/page3")
def page3():
    with data_lock: # 代入中に値が変更されないようロック
        cafe_data = data.cafe
    menu_row = cafe_data.get("menus", [])

    if not menu_row:
        menu_row = [
            {
                "name": "最新情報はありません",
                "price": 0,
                "date": cafe_data.get("generated_at","")
            }
        ]
    
    # 日付順にメニューを並べ替える
    menu_row = sorted(menu_row, key=lambda x: x.get("date", "3000-01-01"))

    return render_template(
        html_url_3,
        menu_row=menu_row
        )


if __name__ == "__main__":
    main()
