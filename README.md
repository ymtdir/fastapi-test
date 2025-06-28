# fastapi-ci-sample

FastAPI アプリケーションの学習用サンプルプロジェクトです。

## セットアップ手順

### 1. 仮想環境の作成

```bash
python3 -m venv venv
```

### 2. 仮想環境の有効化

```bash
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 4. アプリケーションの起動

```bash
uvicorn main:app --reload
```

## 動作確認

- アプリケーション: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### API エンドポイント

- `GET /` - Hello World メッセージを返します
- `POST /add` - 2 つの数値を加算します（JSON 形式）

### 型ヒントによる自動バリデーション

FastAPI は型ヒントを使用して自動的にリクエストデータを検証します：

```python
class AddRequest(BaseModel):
    a: float  # 数値以外が送信されるとバリデーションエラー
    b: float
```

### Swagger UI での確認手順

1. http://localhost:8000/docs にアクセス
2. `POST /add` エンドポイントをクリック
3. 「Try it out」ボタンをクリック
4. リクエストボディに以下を入力：
   ```json
   {
     "a": 10.5,
     "b": 20.3
   }
   ```
5. 「Execute」ボタンをクリック
6. レスポンスを確認

### バリデーションエラーの確認

**無効なデータの例:**

```json
{
  "a": "invalid",
  "b": 20.3
}
```

上記のように文字列を送信すると、FastAPI が自動的にエラーを返します。

### クライアントスクリプトでの確認

別のターミナルを開いて以下を実行：

```bash
python client.py
```

期待される出力：

```
FastAPI サーバーを呼び出しています...
API 呼び出し成功!
レスポンス: {'message': 'Hello, World!'}

=== 加算エンドポイントのテスト ===
POST /add 成功!
リクエスト: {'a': 10.5, 'b': 20.3}
レスポンス: {'a': 10.5, 'b': 20.3, 'result': 30.8, 'message': '10.5 + 20.3 = 30.8'}

=== バリデーションエラーのテスト ===
無効なデータ: {'a': 'invalid', 'b': 20.3}
ステータスコード: 422
エラーレスポンス: {'detail': [{'loc': ['body', 'a'], 'msg': 'value is not a valid float', 'type': 'type_error.float'}]}
```

## ファイル構成

```
fastapi-ci-sample/
├── main.py           # FastAPI アプリケーション
├── client.py         # API クライアントスクリプト
├── requirements.txt  # 依存関係
└── README.md         # このファイル
```

## 仮想環境の無効化

作業終了後は以下のコマンドで仮想環境を無効化できます：

```bash
deactivate
```
