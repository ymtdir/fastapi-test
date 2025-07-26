"""データベース接続設定

最低限のSQLAlchemy設定
"""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# データベース接続URL
DATABASE_URL = "postgresql://user:password@db:5432/fastapi-test"

# SQLAlchemyエンジンの作成
engine = create_engine(DATABASE_URL)

# セッションファクトリーの作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Baseクラス
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """データベースセッションを取得する依存性注入関数"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """テーブルを作成する関数"""
    # モデルをインポートしてテーブルを作成
    from models.user import User

    Base.metadata.create_all(bind=engine)
