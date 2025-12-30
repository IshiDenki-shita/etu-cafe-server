
〜松本VPSでやること〜
・スマホからのPOSTを受け取る
・受け取った献立表.jsonを ルート/hisotry にセーブする
・斎藤VPSに献立表jsonをPOSTする

松本VPSの機能は、
@app.post(/menu_post)
def receive_menu_json():
の中身が全てです。

postを受け取った時に斎藤VPSへの送信もバックアップも全て行う


〜JSONの形式〜
{
    "menu1": {"name": "ダミー担々麺", "price": 200, "date": '2026-1-20'},
    "menu2": {"name": "ダミー春巻き", "price": 300, "date": '2026-1-21'},
}

〜VPSが起動している時間〜
未定
