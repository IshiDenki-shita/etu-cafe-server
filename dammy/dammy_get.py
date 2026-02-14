# macからflaskr.pyへGETリクエストを送って、機能を確かめる

import requests

# 松本VPSへのURL
url = "http://133.242.22.254:8081/menu_get"
# url = "http://210.131.216.51:22/menu_get"
# url = "http://127.0.0.1:8080/menu_get"


def get_dammy_menu(url):
    res = requests.get(url)

    print("\nステータスコード\n")
    print(res.status_code)

    print("\nレスポンス本文\n")
    print(res.text)


def main():
    print("\nGETを投げます\n")

    get_dammy_menu(url)


main()
