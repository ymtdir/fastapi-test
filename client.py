import requests


def call_api():
    """FastAPI サーバーのルートエンドポイントを呼び出す"""
    try:
        # FastAPI サーバーのエンドポイントを呼び出し
        response = requests.get("http://localhost:8000/")

        # ステータスコードを確認
        if response.status_code == 200:
            print("API 呼び出し成功!")
            print(f"レスポンス: {response.json()}")
        else:
            print(f"API 呼び出し失敗: ステータスコード {response.status_code}")

    except requests.exceptions.ConnectionError:
        print(
            "サーバーに接続できませんでした。FastAPI サーバーが起動しているか確認してください。"
        )
    except Exception as e:
        print(f"エラーが発生しました: {e}")


if __name__ == "__main__":
    print("FastAPI サーバーを呼び出しています...")
    call_api()
