
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
jsonは、特別メニューの名前とそれが提供される日付を含む
{
    "generated_at": "2025-12-30T23:19:51+09:00",
    "menus": [
        {"name": "ダミー担々麺", "date": "2026-01-20", "price": 500},
        {"name": "ダミー春巻き", "date": "2026-01-21", "price": 130}
    ]
}
jsonは順序に意味を持たせない方が安全らしい


〜VPSが起動している時間〜
未定
