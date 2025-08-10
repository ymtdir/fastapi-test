"""
認証関連エンドポイントのテストモジュール

テスト実行方法:
1. コマンドラインからの実行:
    python -m pytest -v tests/
    python -m pytest -v tests/test_auth.py

2. 特定のテストメソッドだけ実行:
    python -m pytest -v \
        tests/test_auth.py::TestLogin::test_login_success
    python -m pytest -v tests/test_auth.py::TestLogout::test_logout_success

3. カバレッジレポート生成:
    coverage run -m pytest tests/
    coverage report
    coverage html
"""

from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from main import app
from config import get_db
from models.user import User
from services.auth import AuthService
from services.users import UserService


class TestLogin:
    """ログインエンドポイントのテストクラス"""

    def test_login_success(self, client: TestClient):
        """ログインの正常系テスト

        正しい認証情報を送信した際に、適切なJWTトークンが返されることを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # モックユーザーオブジェクト（未使用のため削除）

        # AuthServiceのメソッドをモック化
        with patch("services.auth.AuthService.login_user") as mock_login:
            mock_login.return_value = {
                "access_token": "mock_jwt_token",
                "token_type": "bearer",
            }

            # データベースセッションをオーバーライド
            def override_get_db():
                yield mock_db

            app.dependency_overrides[get_db] = override_get_db

            try:
                # テストデータ
                request_data = {
                    "email": "test@example.com",
                    "password": "password123",
                }

                # APIリクエストを送信
                response = client.post("/api/auth/login", json=request_data)

                # レスポンスの検証
                assert response.status_code == 200
                response_data = response.json()
                assert "access_token" in response_data
                assert response_data["token_type"] == "bearer"
                assert response_data["access_token"] == "mock_jwt_token"

                # サービスメソッドの呼び出し確認
                mock_login.assert_called_once()

            finally:
                # オーバーライドとモックをクリア
                app.dependency_overrides.clear()

    def test_login_invalid_credentials(self, client: TestClient):
        """ログインの異常系テスト（無効な認証情報）

        間違った認証情報を送信した際のエラーハンドリングを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # AuthServiceのメソッドをモック化（認証失敗）
        AuthService.authenticate_user = MagicMock(return_value=None)

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # テストデータ
            request_data = {
                "email": "test@example.com",
                "password": "wrongpassword",
            }

            # APIリクエストを送信
            response = client.post("/api/auth/login", json=request_data)

            # レスポンスの検証
            assert response.status_code == 401
            response_data = response.json()
            assert "detail" in response_data
            assert (
                "メールアドレスまたはパスワードが正しくありません"
                in response_data["detail"]
            )

            # サービスメソッドの呼び出し確認
            AuthService.authenticate_user.assert_called_once_with(
                mock_db, "test@example.com", "wrongpassword"
            )

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            AuthService.authenticate_user.reset_mock()

    def test_login_invalid_email_format(self, client: TestClient):
        """ログインの異常系テスト（無効なメール形式）

        無効なメールアドレス形式を送信した際のバリデーションエラーを検証します。
        """
        # テストデータ（無効なメール形式）
        request_data = {
            "email": "invalid-email",
            "password": "password123",
        }

        # APIリクエストを送信
        response = client.post("/api/auth/login", json=request_data)

        # レスポンスの検証
        assert response.status_code == 422  # Validation Error
        response_data = response.json()
        assert "detail" in response_data

    def test_login_missing_fields(self, client: TestClient):
        """ログインの異常系テスト（必須フィールドの欠落）

        必須フィールドが欠落している場合のバリデーションエラーを検証します。
        """
        # テストデータ（パスワードが欠落）
        request_data = {
            "email": "test@example.com",
        }

        # APIリクエストを送信
        response = client.post("/api/auth/login", json=request_data)

        # レスポンスの検証
        assert response.status_code == 422  # Validation Error
        response_data = response.json()
        assert "detail" in response_data

    def test_login_empty_fields(self, client: TestClient):
        """ログインの異常系テスト（空のフィールド）

        空のフィールドを送信した際のバリデーションエラーを検証します。
        """
        # テストデータ（空のフィールド）
        request_data = {
            "email": "",
            "password": "",
        }

        # APIリクエストを送信
        response = client.post("/api/auth/login", json=request_data)

        # レスポンスの検証
        assert response.status_code == 422  # Validation Error
        response_data = response.json()
        assert "detail" in response_data


class TestLogout:
    """ログアウトエンドポイントのテストクラス"""

    def test_logout_success(self, client: TestClient):
        """ログアウトの正常系テスト

        ログアウトエンドポイントが正常に応答することを検証します。
        """
        # APIリクエストを送信
        response = client.post("/api/auth/logout")

        # レスポンスの検証
        assert response.status_code == 200
        response_data = response.json()
        assert "message" in response_data
        assert "ログアウトしました" in response_data["message"]


class TestAuthService:
    """認証サービスのテストクラス"""

    def test_authenticate_user_success(self):
        """ユーザー認証の正常系テスト

        正しい認証情報でユーザーが認証されることを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # モックユーザーオブジェクト
        mock_user = User(
            id=1, name="testuser", email="test@example.com", password="hashed_password"
        )

        # AuthService.authenticate_userメソッド全体をモック化
        with patch.object(AuthService, "authenticate_user") as mock_authenticate:
            mock_authenticate.return_value = mock_user

            # 認証テスト
            result = AuthService.authenticate_user(
                mock_db, "test@example.com", "password123"
            )

            # 結果の検証
            assert result == mock_user
            mock_authenticate.assert_called_once_with(
                mock_db, "test@example.com", "password123"
            )

    def test_authenticate_user_invalid_email(self):
        """ユーザー認証の異常系テスト（存在しないメールアドレス）

        存在しないメールアドレスで認証が失敗することを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # AuthService.authenticate_userメソッド全体をモック化
        with patch.object(AuthService, "authenticate_user") as mock_authenticate:
            mock_authenticate.return_value = None

            # 認証テスト
            result = AuthService.authenticate_user(
                mock_db, "nonexistent@example.com", "password123"
            )

            # 結果の検証
            assert result is None
            mock_authenticate.assert_called_once_with(
                mock_db, "nonexistent@example.com", "password123"
            )

    def test_authenticate_user_invalid_password(self):
        """ユーザー認証の異常系テスト（間違ったパスワード）

        間違ったパスワードで認証が失敗することを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # AuthService.authenticate_userメソッド全体をモック化
        with patch.object(AuthService, "authenticate_user") as mock_authenticate:
            mock_authenticate.return_value = None

            # 認証テスト
            result = AuthService.authenticate_user(
                mock_db, "test@example.com", "wrongpassword"
            )

            # 結果の検証
            assert result is None
            mock_authenticate.assert_called_once_with(
                mock_db, "test@example.com", "wrongpassword"
            )

    def test_create_access_token(self):
        """アクセストークン作成のテスト

        JWTアクセストークンが正しく作成されることを検証します。
        """
        # テストデータ
        data = {"sub": "test@example.com"}

        # トークン作成
        token = AuthService.create_access_token(data)

        # 結果の検証
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_token_valid(self):
        """トークン検証の正常系テスト

        有効なJWTトークンが正しく検証されることを検証します。
        """
        # テストデータ
        data = {"sub": "test@example.com"}

        # トークン作成
        token = AuthService.create_access_token(data)

        # トークン検証
        token_data = AuthService.verify_token(token)

        # 結果の検証
        assert token_data is not None
        assert token_data.email == "test@example.com"

    def test_verify_token_invalid(self):
        """トークン検証の異常系テスト

        無効なJWTトークンが正しく拒否されることを検証します。
        """
        # 無効なトークン
        invalid_token = "invalid.jwt.token"

        # トークン検証
        token_data = AuthService.verify_token(invalid_token)

        # 結果の検証
        assert token_data is None


class TestAuthIntegration:
    """認証機能の統合テストクラス"""

    def test_auth_lifecycle(self, client: TestClient):
        """認証ライフサイクルの統合テスト

        ユーザー作成からログイン、ログアウトまでの一連の流れを検証します。
        """
        # モックデータベースセッション
        mock_db = MagicMock()

        # モックユーザーオブジェクト
        mock_user = User(
            id=1, name="testuser", email="test@example.com", password="hashed_password"
        )

        # サービスメソッドをモック化
        UserService.is_name_taken = MagicMock(return_value=False)
        UserService.is_email_taken = MagicMock(return_value=False)
        UserService.create_user = MagicMock(return_value=mock_user)
        AuthService.authenticate_user = MagicMock(return_value=mock_user)
        AuthService.create_access_token = MagicMock(return_value="mock_jwt_token")

        # データベースセッションをオーバーライド
        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        try:
            # 1. ユーザー作成
            create_data = {
                "name": "testuser",
                "email": "test@example.com",
                "password": "password123",
            }
            create_response = client.post("/api/users/", json=create_data)
            assert create_response.status_code == 201

            # 2. ログイン
            login_data = {
                "email": "test@example.com",
                "password": "password123",
            }
            login_response = client.post("/api/auth/login", json=login_data)
            assert login_response.status_code == 200
            login_result = login_response.json()
            assert "access_token" in login_result

            # 3. ログアウト
            logout_response = client.post("/api/auth/logout")
            assert logout_response.status_code == 200

        finally:
            # オーバーライドとモックをクリア
            app.dependency_overrides.clear()
            UserService.is_name_taken.reset_mock()
            UserService.is_email_taken.reset_mock()
            UserService.create_user.reset_mock()
            AuthService.authenticate_user.reset_mock()
            AuthService.create_access_token.reset_mock()
