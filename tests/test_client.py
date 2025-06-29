import pytest
import requests
from unittest.mock import patch, Mock

import client


def test_call_api_success():
    """API呼び出し成功のテスト"""
    # モックレスポンスを作成
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"message": "Hello, World!"}

    with patch("requests.get", return_value=mock_response) as mock_get:
        with patch("builtins.print") as mock_print:
            client.call_api()

            # requests.getが正しいURLで呼ばれたか確認
            mock_get.assert_called_once_with("http://localhost:8000/")

            # 成功メッセージが出力されたか確認
            mock_print.assert_any_call("API 呼び出し成功!")
            mock_print.assert_any_call("レスポンス: {'message': 'Hello, World!'}")


def test_call_api_failure_status():
    """API呼び出し失敗（ステータスコードエラー）のテスト"""
    # モックレスポンスを作成
    mock_response = Mock()
    mock_response.status_code = 404

    with patch("requests.get", return_value=mock_response) as mock_get:
        with patch("builtins.print") as mock_print:
            client.call_api()

            # requests.getが呼ばれたか確認
            mock_get.assert_called_once_with("http://localhost:8000/")

            # エラーメッセージが出力されたか確認
            mock_print.assert_any_call("API 呼び出し失敗: ステータスコード 404")


def test_call_api_connection_error():
    """API呼び出し失敗（接続エラー）のテスト"""
    with patch(
        "requests.get", side_effect=requests.exceptions.ConnectionError()
    ) as mock_get:
        with patch("builtins.print") as mock_print:
            client.call_api()

            # requests.getが呼ばれたか確認
            mock_get.assert_called_once_with("http://localhost:8000/")

            # 接続エラーメッセージが出力されたか確認
            mock_print.assert_any_call(
                "サーバーに接続できませんでした。FastAPI サーバーが起動しているか確認してください。"
            )


def test_call_api_general_exception():
    """API呼び出し失敗（一般的な例外）のテスト"""
    with patch("requests.get", side_effect=Exception("テストエラー")) as mock_get:
        with patch("builtins.print") as mock_print:
            client.call_api()

            # requests.getが呼ばれたか確認
            mock_get.assert_called_once_with("http://localhost:8000/")

            # 一般エラーメッセージが出力されたか確認
            mock_print.assert_any_call("エラーが発生しました: テストエラー")
