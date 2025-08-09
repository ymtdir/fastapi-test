"""認証関連のPydanticスキーマ

JWT認証とログイン機能のリクエスト/レスポンスのバリデーションとシリアライゼーションを行います。
"""

from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class UserLogin(BaseModel):
    """ユーザーログイン用スキーマ

    POSTリクエストで受け取るログインデータの形式を定義します。

    Attributes:
        email: メールアドレス（必須、有効なメール形式）
        password: パスワード（必須）
    """

    email: EmailStr = Field(..., description="メールアドレス")
    password: str = Field(..., description="パスワード")

    class Config:
        """設定クラス"""

        # JSON Schema用のサンプルデータ
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "P@ssw0rd",
            }
        }


class Token(BaseModel):
    """認証トークン用スキーマ

    JWTトークンのレスポンス形式を定義します。

    Attributes:
        access_token: アクセストークン
        token_type: トークンタイプ（通常は"bearer"）
    """

    access_token: str = Field(..., description="アクセストークン")
    token_type: str = Field(default="bearer", description="トークンタイプ")

    class Config:
        """設定クラス"""

        # JSON Schema用のサンプルデータ
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
            }
        }


class TokenData(BaseModel):
    """トークンデータ用スキーマ

    JWTトークンに含まれるデータの形式を定義します。

    Attributes:
        email: メールアドレス（オプション）
    """

    email: Optional[str] = None
