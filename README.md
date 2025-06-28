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

### Swagger UI での確認手順

1. http://localhost:8000/docs にアクセス
2. `GET /` エンドポイントをクリック
3. 「Try it out」ボタンをクリック
4. 「Execute」ボタンをクリック
5. レスポンスを確認

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
