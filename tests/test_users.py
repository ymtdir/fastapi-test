"""
ユーザー関連エンドポイントのテストモジュール

テスト実行方法:
1. コマンドラインからの実行:
    python -m pytest -v tests/
    python -m pytest -v tests/test_users.py

2. 特定のテストメソッドだけ実行:
    python -m pytest -v \
        tests/test_users.py::TestCreateUser::test_create_user_success
    python -m pytest -v tests/test_users.py::TestGetUser::test_get_user_success

3. カバレッジレポート生成:
    coverage run -m pytest tests/
    coverage report
    coverage html
"""

from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

from main import app
from config import get_db
from models.user import User
from services.users import UserService


class TestCreateUser:
    """ユーザー作成エンドポイントのテストクラス"""

    def test_create_user_success(self, client: TestClient):
        """ユーザー作成の正常系テスト

        正常なユーザーデータを送信した際に、適切なレスポンスが返されることを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # モックユーザーオブジェクト
        mock_user = User(
            id=1, name="testuser", email="test@example.com", password="hashed_password"
        )

        # UserServiceのメソッドをモック化
        UserService.is_name_taken = MagicMock(return_value=False)
        UserService.is_email_taken = MagicMock(return_value=False)
        UserService.create_user = MagicMock(return_value=mock_user)

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        # データベースセッションをオーバーライド
        app.dependency_overrides[get_db] = override_get_db

        try:
            # テストデータ
            request_data = {
                "name": "testuser",
                "email": "test@example.com",
                "password": "password123",
            }

            # APIリクエストを送信
            response = client.post("/api/users/", json=request_data)

            # レスポンスの検証
            assert response.status_code == 201
            response_data = response.json()
            assert response_data["id"] == 1
            assert response_data["name"] == "testuser"
            assert response_data["email"] == "test@example.com"
            assert "password" not in response_data  # パスワードは含まれない

            # サービスメソッドの呼び出し確認
            UserService.is_name_taken.assert_called_once_with(mock_db, "testuser")
            UserService.is_email_taken.assert_called_once_with(
                mock_db, "test@example.com"
            )
            UserService.create_user.assert_called_once()

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            UserService.is_name_taken.reset_mock()
            UserService.is_email_taken.reset_mock()
            UserService.create_user.reset_mock()

    def test_create_user_duplicate_name(self, client: TestClient):
        """ユーザー作成の異常系テスト（重複するユーザー名）

        既に存在するユーザー名を使用した場合のエラーハンドリングを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # UserServiceのメソッドをモック化（ユーザー名重複）
        UserService.is_name_taken = MagicMock(return_value=True)
        UserService.is_email_taken = MagicMock(return_value=False)

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # テストデータ
            request_data = {
                "name": "existinguser",
                "email": "new@example.com",
                "password": "password123",
            }

            # APIリクエストを送信
            response = client.post("/api/users/", json=request_data)

            # エラーレスポンスの検証
            assert response.status_code == 400
            response_data = response.json()
            assert "existinguser" in response_data["detail"]
            assert "既に使用されています" in response_data["detail"]

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            UserService.is_name_taken.reset_mock()
            UserService.is_email_taken.reset_mock()

    def test_create_user_duplicate_email(self, client: TestClient):
        """ユーザー作成の異常系テスト（重複するメールアドレス）

        既に存在するメールアドレスを使用した場合のエラーハンドリングを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # UserServiceのメソッドをモック化（メール重複）
        UserService.is_name_taken = MagicMock(return_value=False)
        UserService.is_email_taken = MagicMock(return_value=True)

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # テストデータ
            request_data = {
                "name": "newuser",
                "email": "existing@example.com",
                "password": "password123",
            }

            # APIリクエストを送信
            response = client.post("/api/users/", json=request_data)

            # エラーレスポンスの検証
            assert response.status_code == 400
            response_data = response.json()
            assert "existing@example.com" in response_data["detail"]
            assert "既に使用されています" in response_data["detail"]

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            UserService.is_name_taken.reset_mock()
            UserService.is_email_taken.reset_mock()

    def test_create_user_invalid_data(self, client: TestClient):
        """ユーザー作成の異常系テスト（不正なデータ）

        バリデーションエラーが発生するデータを送信した場合のエラーハンドリングを検証します。
        """
        # 不正なリクエストデータ（nameフィールドが不足）
        invalid_request_data = {"email": "test@example.com", "password": "password123"}

        # APIリクエストを送信
        response = client.post("/api/users/", json=invalid_request_data)

        # バリデーションエラーの検証
        assert response.status_code == 422
        response_data = response.json()
        assert "detail" in response_data

        # nameフィールドが不足している旨のエラーを確認
        errors = response_data["detail"]
        assert any(error["loc"] == ["body", "name"] for error in errors)

    def test_create_user_short_password(self, client: TestClient):
        """ユーザー作成の異常系テスト（短すぎるパスワード）

        パスワードが8文字未満の場合のバリデーションエラーを検証します。
        """
        # 短いパスワードのテストデータ
        request_data = {
            "name": "testuser",
            "email": "test@example.com",
            "password": "123",  # 8文字未満
        }

        # APIリクエストを送信
        response = client.post("/api/users/", json=request_data)

        # バリデーションエラーの検証
        assert response.status_code == 422
        response_data = response.json()
        assert "detail" in response_data

        # パスワードの長さに関するエラーを確認
        errors = response_data["detail"]
        assert any(error["loc"] == ["body", "password"] for error in errors)

    def test_create_user_integrity_error(self, client: TestClient):
        """ユーザー作成の異常系テスト（データベース制約エラー）

        データベースレベルでの制約違反が発生した場合のエラーハンドリングを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # UserServiceのメソッドをモック化
        UserService.is_name_taken = MagicMock(return_value=False)
        UserService.is_email_taken = MagicMock(return_value=False)
        UserService.create_user = MagicMock(side_effect=IntegrityError("", "", ""))

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # テストデータ
            request_data = {
                "name": "testuser",
                "email": "test@example.com",
                "password": "password123",
            }

            # APIリクエストを送信
            response = client.post("/api/users/", json=request_data)

            # エラーレスポンスの検証
            assert response.status_code == 400
            response_data = response.json()
            assert "既に使用されています" in response_data["detail"]

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            UserService.is_name_taken.reset_mock()
            UserService.is_email_taken.reset_mock()
            UserService.create_user.reset_mock()
