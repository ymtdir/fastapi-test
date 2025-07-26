"""
Pytest設定とフィクスチャ

FastAPIアプリケーションのテスト用設定とフィクスチャを定義します。

注意事項:
    ファイル名'conftest.py'はpytestの規約で固定されており、変更できません。
    pytestがこのファイルを自動で発見・読み込みします。

実行方法:
    cd backend
    pip install -r requirements.txt
    python -m pytest tests/test_health.py -v
"""

import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    """FastAPIアプリケーション用のテストクライアントを作成

    FastAPIアプリケーションに対してHTTPリクエストを送信するための
    TestClientインスタンスを提供するフィクスチャです。

    Returns:
        TestClient: 設定済みのFastAPIアプリ用テストクライアント

    使用例:
        def test_endpoint(client):
            response = client.get("/")
            assert response.status_code == 200
    """
    return TestClient(app)
