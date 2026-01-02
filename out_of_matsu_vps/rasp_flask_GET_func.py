# ラズパイに入れる、rasp_html_cafe.htmlにreturnするflask関数

from flask import Flask, json, request, render_template
from dataclasses import dataclass

app = Flask(__file__)

# 食堂メニューの取り扱いに関するクラス
@dataclass
class cafe:
    latest_menu_data : bytes # GETで取得したデータ
    latest_menu_dict : dict # 取得したjsonを辞書に展開したもの
# 実際に宣言
cafe1 = cafe(b"", {})

# 斎藤VPSからGETしてきた食堂メニューデータ（ダミー）

# メニューデータの開封後(ダミー)
cafe1.latest_menu_dict = {
    "generated_at": "2025-12-30T23:19:51+09:00",
    "menus": [
        {"name": "ダミー担々麺", "date": "2026-01-20", "price": 500},
        {"name": "ダミー春巻き", "date": "2026-01-21", "price": 130},
    ],
}

@app.get("/menu_cafe")
def page_menu():
    menu_row = cafe1.latest_menu_dict["menus"]

    return render_template(
        "templates/rasp_html_cafe.html",
        menu_row = menu_row
    )
