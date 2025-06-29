from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_read_root():
    """ルートエンドポイントのテスト"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}


def test_add_numbers_success():
    """加算エンドポイントの正常ケーステスト"""
    test_data = {"a": 10.5, "b": 20.3}
    response = client.post("/add", json=test_data)

    assert response.status_code == 200
    result = response.json()
    assert result["a"] == 10.5
    assert result["b"] == 20.3
    assert result["result"] == 30.8
    assert "message" in result


def test_add_numbers_zero():
    """ゼロを含む加算のテスト"""
    test_data = {"a": 0, "b": 5.5}
    response = client.post("/add", json=test_data)

    assert response.status_code == 200
    result = response.json()
    assert result["result"] == 5.5
