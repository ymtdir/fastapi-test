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
            UserService.is_email_taken.assert_called_once_with(
                mock_db, "test@example.com"
            )
            UserService.create_user.assert_called_once()

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            UserService.is_email_taken.reset_mock()
            UserService.create_user.reset_mock()

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
            UserService.is_email_taken.reset_mock()
            UserService.create_user.reset_mock()


class TestGetUsers:
    """ユーザー一覧取得エンドポイントのテストクラス"""

    def test_get_users_success(self, client: TestClient):
        """ユーザー一覧取得の正常系テスト

        正常にユーザー一覧が取得できることを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # モックユーザーリスト
        mock_users = [
            User(id=1, name="user1", email="user1@example.com", password="hashed1"),
            User(id=2, name="user2", email="user2@example.com", password="hashed2"),
        ]

        # UserServiceのメソッドをモック化
        UserService.get_all_users = MagicMock(return_value=mock_users)

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # APIリクエストを送信
            response = client.get("/api/users/")

            # レスポンスの検証
            assert response.status_code == 200
            response_data = response.json()
            assert len(response_data) == 2
            assert response_data[0]["id"] == 1
            assert response_data[0]["name"] == "user1"
            assert response_data[0]["email"] == "user1@example.com"
            assert response_data[1]["id"] == 2
            assert response_data[1]["name"] == "user2"
            assert response_data[1]["email"] == "user2@example.com"

            # パスワードが含まれていないことを確認
            for user in response_data:
                assert "password" not in user

            # サービスメソッドの呼び出し確認
            UserService.get_all_users.assert_called_once_with(mock_db)

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            UserService.get_all_users.reset_mock()


class TestGetUser:
    """ユーザー詳細取得エンドポイントのテストクラス"""

    def test_get_user_success(self, client: TestClient):
        """ユーザー詳細取得の正常系テスト

        存在するユーザーIDで正常にユーザー詳細が取得できることを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # モックユーザーオブジェクト
        mock_user = User(
            id=1, name="testuser", email="test@example.com", password="hashed_password"
        )

        # UserServiceのメソッドをモック化
        UserService.get_user_by_id = MagicMock(return_value=mock_user)

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # APIリクエストを送信
            response = client.get("/api/users/1")

            # レスポンスの検証
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["id"] == 1
            assert response_data["name"] == "testuser"
            assert response_data["email"] == "test@example.com"
            assert "password" not in response_data  # パスワードは含まれない

            # サービスメソッドの呼び出し確認
            UserService.get_user_by_id.assert_called_once_with(mock_db, 1)

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            UserService.get_user_by_id.reset_mock()

    def test_get_user_not_found(self, client: TestClient):
        """ユーザー詳細取得の異常系テスト（ユーザーが存在しない）

        存在しないユーザーIDでリクエストした場合のエラーハンドリングを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # UserServiceのメソッドをモック化（ユーザーが見つからない）
        UserService.get_user_by_id = MagicMock(return_value=None)

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # APIリクエストを送信
            response = client.get("/api/users/999")

            # エラーレスポンスの検証
            assert response.status_code == 404
            response_data = response.json()
            assert "999" in response_data["detail"]
            assert "見つかりません" in response_data["detail"]

            # サービスメソッドの呼び出し確認
            UserService.get_user_by_id.assert_called_once_with(mock_db, 999)

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            UserService.get_user_by_id.reset_mock()


class TestUpdateUser:
    """ユーザー更新エンドポイントのテストクラス"""

    def test_update_user_info_success(self, client: TestClient):
        """ユーザー情報更新の正常系テスト（パスワード変更なし）

        名前とメールアドレスのみを更新した場合の正常系を検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # モックユーザーオブジェクト（更新後）
        mock_updated_user = User(
            id=1,
            name="updated_user",
            email="updated@example.com",
            password="hashed_password",
        )

        # UserServiceのメソッドをモック化
        UserService.update_user = MagicMock(return_value=mock_updated_user)

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # テストデータ（パスワード変更なし）
            request_data = {
                "name": "updated_user",
                "email": "updated@example.com",
            }

            # APIリクエストを送信
            response = client.put("/api/users/1", json=request_data)

            # レスポンスの検証
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["id"] == 1
            assert response_data["name"] == "updated_user"
            assert response_data["email"] == "updated@example.com"
            assert "password" not in response_data

            # サービスメソッドの呼び出し確認
            UserService.update_user.assert_called_once()

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            UserService.update_user.reset_mock()

    def test_update_user_password_success(self, client: TestClient):
        """ユーザーパスワード更新の正常系テスト

        パスワードのみを更新した場合の正常系を検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # モックユーザーオブジェクト（更新後）
        mock_updated_user = User(
            id=1,
            name="testuser",
            email="test@example.com",
            password="new_hashed_password",
        )

        # UserServiceのメソッドをモック化
        UserService.update_user = MagicMock(return_value=mock_updated_user)

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # テストデータ（パスワード変更のみ）
            request_data = {
                "current_password": "oldpassword",
                "new_password": "newpassword123",
            }

            # APIリクエストを送信
            response = client.put("/api/users/1", json=request_data)

            # レスポンスの検証
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["id"] == 1
            assert response_data["name"] == "testuser"
            assert response_data["email"] == "test@example.com"
            assert "password" not in response_data

            # サービスメソッドの呼び出し確認
            UserService.update_user.assert_called_once()

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            UserService.update_user.reset_mock()

    def test_update_user_not_found(self, client: TestClient):
        """ユーザー更新の異常系テスト（ユーザーが存在しない）

        存在しないユーザーIDで更新リクエストした場合のエラーハンドリングを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # UserServiceのメソッドをモック化（ユーザーが見つからない）
        UserService.update_user = MagicMock(return_value=None)

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # テストデータ
            request_data = {
                "name": "updated_user",
            }

            # APIリクエストを送信
            response = client.put("/api/users/999", json=request_data)

            # エラーレスポンスの検証
            assert response.status_code == 404
            response_data = response.json()
            assert "999" in response_data["detail"]
            assert "見つかりません" in response_data["detail"]

            # サービスメソッドの呼び出し確認
            UserService.update_user.assert_called_once()

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            UserService.update_user.reset_mock()

    def test_update_user_password_error(self, client: TestClient):
        """ユーザー更新の異常系テスト（パスワードエラー）

        現在のパスワードが間違っている場合のエラーハンドリングを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # UserServiceのメソッドをモック化（パスワードエラー）
        UserService.update_user = MagicMock(
            side_effect=ValueError("現在のパスワードが正しくありません")
        )

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # テストデータ（間違った現在のパスワード）
            request_data = {
                "current_password": "wrongpassword",
                "new_password": "newpassword123",
            }

            # APIリクエストを送信
            response = client.put("/api/users/1", json=request_data)

            # エラーレスポンスの検証
            assert response.status_code == 400
            response_data = response.json()
            assert "現在のパスワードが正しくありません" in response_data["detail"]

            # サービスメソッドの呼び出し確認
            UserService.update_user.assert_called_once()

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            UserService.update_user.reset_mock()

    def test_update_user_duplicate_error(self, client: TestClient):
        """ユーザー更新の異常系テスト（重複エラー）

        重複するメールアドレスで更新した場合のエラーハンドリングを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # UserServiceのメソッドをモック化（重複エラー）
        UserService.update_user = MagicMock(side_effect=IntegrityError("", "", ""))

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # テストデータ
            request_data = {
                "email": "duplicate@example.com",
            }

            # APIリクエストを送信
            response = client.put("/api/users/1", json=request_data)

            # エラーレスポンスの検証
            assert response.status_code == 400
            response_data = response.json()
            assert "既に使用されています" in response_data["detail"]

            # サービスメソッドの呼び出し確認
            UserService.update_user.assert_called_once()

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            UserService.update_user.reset_mock()


class TestDeleteUser:
    """ユーザー削除エンドポイントのテストクラス"""

    def test_delete_user_success(self, client: TestClient):
        """ユーザー削除の正常系テスト

        存在するユーザーIDで正常にユーザーが削除できることを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # UserServiceのメソッドをモック化
        UserService.delete_user = MagicMock(return_value=True)

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # APIリクエストを送信
            response = client.delete("/api/users/1")

            # レスポンスの検証
            assert response.status_code == 204
            assert response.content == b""  # 空のレスポンスボディ

            # サービスメソッドの呼び出し確認
            UserService.delete_user.assert_called_once_with(mock_db, 1)

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            UserService.delete_user.reset_mock()

    def test_delete_user_not_found(self, client: TestClient):
        """ユーザー削除の異常系テスト（ユーザーが存在しない）

        存在しないユーザーIDで削除リクエストした場合のエラーハンドリングを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # UserServiceのメソッドをモック化（ユーザーが見つからない）
        UserService.delete_user = MagicMock(return_value=False)

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # APIリクエストを送信
            response = client.delete("/api/users/999")

            # エラーレスポンスの検証
            assert response.status_code == 404
            response_data = response.json()
            assert "999" in response_data["detail"]
            assert "見つかりません" in response_data["detail"]

            # サービスメソッドの呼び出し確認
            UserService.delete_user.assert_called_once_with(mock_db, 999)

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            UserService.delete_user.reset_mock()
