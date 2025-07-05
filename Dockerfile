FROM python:3.11-slim

# 作業ディレクトリの設定
WORKDIR /app

# 依存関係をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのコードをコピー
COPY . .

# ポートを公開
EXPOSE 8000

# FastAPIアプリを起動
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 