# fastapi-test

FastAPI アプリケーションと CI/CD パイプラインの学習用サンプルプロジェクトです。

## 🚀 プロジェクト概要

このプロジェクトは以下の技術要素を含む実践的な学習サンプルです：

- **FastAPI** - モダンで高速な Python Web フレームワーク
- **GitHub Actions** - CI/CD パイプライン
- **pytest** - テスト自動化
- **flake8** - コード品質チェック（Lint）
- **pytest-cov** - テストカバレッジ測定

## 📁 プロジェクト構成

```
fastapi-test/
├── main.py                    # FastAPI アプリケーション
├── requirements.txt           # 依存関係
├── Dockerfile                 # Docker イメージ定義
├── docker-compose.yml         # Docker Compose 設定
├── .dockerignore             # Docker ビルドで除外するファイル
├── tests/                     # テストコード
│   ├── __init__.py
│   └── test_main.py          # メインアプリのテスト
├── .github/
│   └── workflows/
│       └── ci.yml            # GitHub Actions CI設定
├── .gitignore
└── README.md                 # このファイル
```

## 🛠️ セットアップ手順

### Docker を使用した起動（推奨）

```bash
# Docker Compose を使用した起動
docker-compose up --build

# デタッチモードで起動
docker-compose up -d --build
```

### ローカル環境での起動

```bash
# 1. 仮想環境の作成
python3 -m venv venv

# 2. 仮想環境の有効化
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate

# 3. 依存関係のインストール
pip install -r requirements.txt

# 4. アプリケーションの起動
uvicorn main:app --reload
```

## 🔍 動作確認

### Web インターフェース

- **アプリケーション**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### API エンドポイント

- `GET /` - Hello World メッセージを返します
- `POST /add` - 2 つの数値を加算します（JSON 形式）

### 🐳 Docker コマンド

```bash
# Docker イメージのビルド
docker build -t fastapi-app .

# Docker コンテナの起動
docker run -p 8000:8000 fastapi-app

# Docker Compose での起動
docker-compose up --build

# Docker Compose でバックグラウンド起動
docker-compose up -d

# Docker Compose で停止
docker-compose down

# ログの確認
docker-compose logs -f
```

## 🧪 テスト実行

### 基本的なテスト実行

```bash
# 全てのテストを実行
pytest tests/ -v

# 特定のテストファイルを実行
pytest tests/test_main.py -v
```

### カバレッジ測定

```bash
# カバレッジレポート付きでテスト実行
pytest tests/ --cov=. --cov-report=term

# HTML形式のカバレッジレポート生成
pytest tests/ --cov=. --cov-report=html
# htmlcov/index.html をブラウザで開いてレポート確認
```

### コード品質チェック（Lint）

```bash
# 全ファイルのLintチェック
flake8 . --max-line-length=88 --exclude=venv,__pycache__,.git

# 特定のファイルのみチェック
flake8 main.py client.py
```

## 🔄 CI/CD パイプライン

このプロジェクトでは GitHub Actions を使用して CI/CD パイプラインを構築しています。

### 自動実行されるチェック

1. **テスト実行** - pytest による全テストの実行
2. **Lint チェック** - flake8 によるコード品質チェック
3. **カバレッジ測定** - 80% 以上のテストカバレッジを要求

### トリガー条件

- `main`, `develop` ブランチへのプッシュ
- `main` ブランチへのプルリクエスト

### ブランチ保護

`main` ブランチは以下のルールで保護されています：

- CI チェック（test / lint / coverage）が全て成功しないとマージ不可
- 強制プッシュ（`--force`）の禁止
- ブランチの削除禁止

## 🎯 学習ポイント

このプロジェクトを通じて以下を学習できます：

### 1. FastAPI の基本機能

- 型ヒントによる自動バリデーション
- Swagger UI による API ドキュメント自動生成
- Pydantic モデルを使用したデータ検証

### 2. テスト自動化

- FastAPI アプリケーションのテスト方法
- モックを使用した外部依存関係のテスト
- テストカバレッジの測定と改善

### 3. CI/CD パイプライン

- GitHub Actions を使用した自動テスト
- コード品質チェック（Lint）の自動化
- ブランチ保護ルールによる品質担保

### 4. 開発ワークフロー

- 「失敗 → 修正 → 成功」のサイクルによる学習
- プルリクエストベースの開発フロー
- コード品質の継続的な改善

## 📊 品質指標

現在のプロジェクト品質：

- **テストカバレッジ**: 98%
- **Lint エラー**: 0 件
- **テスト成功率**: 100% (7/7 テスト)

## 💡 使用方法

### 開発ワークフロー

```bash
# 1. 機能ブランチを作成
git checkout -b feature/new-feature

# 2. コード変更 & テスト追加
# ... 開発作業 ...

# 3. ローカルでテスト実行
pytest tests/ --cov=. --cov-report=term
flake8 . --max-line-length=88 --exclude=venv,__pycache__,.git

# 4. コミット & プッシュ
git add .
git commit -m "Add new feature"
git push origin feature/new-feature

# 5. GitHub で PR 作成 → CI 自動実行 → マージ
```

### バリデーションエラーの確認

Swagger UI (http://localhost:8000/docs) で以下を試してみてください：

**正常なリクエスト例:**

```json
{
  "a": 10.5,
  "b": 20.3
}
```

**エラーになるリクエスト例:**

```json
{
  "a": "invalid",
  "b": 20.3
}
```

## 🏁 終了時の処理

```bash
# アプリケーション停止: Ctrl+C

# 仮想環境の無効化
deactivate
```

## 📖 参考資料

- [FastAPI 公式ドキュメント](https://fastapi.tiangolo.com/)
- [pytest 公式ドキュメント](https://docs.pytest.org/)
- [GitHub Actions ドキュメント](https://docs.github.com/ja/actions)
