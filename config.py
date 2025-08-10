"""アプリ設定とデータベース接続設定

環境変数から設定を読み込み、SQLAlchemyの最低限のセットアップを提供します。
"""

from typing import Generator
from pydantic import Field
from pydantic_settings import BaseSettings
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session


class Settings(BaseSettings):
    """アプリ全体の設定

    環境変数から値を読み込みます。存在しない場合はデフォルトを使用します。
    """

    # JWT関連
    secret_key: str = Field("change_me", env="SECRET_KEY")
    algorithm: str = Field("HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # DB関連
    database_url: str = Field(
        "postgresql://user:password@db:5432/fastapi-test", env="DATABASE_URL"
    )

    class Config:
        env_file = ".env"
        extra = "ignore"


# グローバル設定インスタンス
settings = Settings()

# データベース接続URL
DATABASE_URL = settings.database_url

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
    from models.user import User  # noqa: F401

    Base.metadata.create_all(bind=engine)
