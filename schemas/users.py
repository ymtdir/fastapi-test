"""ユーザー関連のPydanticスキーマ

リクエスト/レスポンスのバリデーションとシリアライゼーションを行います。
"""

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    """ユーザー作成用スキーマ

    POSTリクエストで受け取るデータの形式を定義します。

    Attributes:
        name: ユーザー名（必須、3-50文字）
        email: メールアドレス（必須、有効なメール形式）
        password: パスワード（必須、8文字以上）
    """

    name: str = Field(..., min_length=3, max_length=50, description="ユーザー名")
    email: str = Field(..., description="メールアドレス")
    password: str = Field(..., min_length=8, description="パスワード")

    class Config:
        """設定クラス"""

        # JSON Schema用のサンプルデータ
        json_schema_extra = {
            "example": {
                "name": "user",
                "email": "user@example.com",
                "password": "P@ssw0rd",
            }
        }


class UserResponse(BaseModel):
    """ユーザーレスポンス用スキーマ

    APIレスポンスで返すデータの形式を定義します。
    セキュリティのためパスワードは含めません。

    Attributes:
        id: ユーザーID
        name: ユーザー名
        email: メールアドレス
    """

    id: int
    name: str
    email: str

    class Config:
        """設定クラス"""

        from_attributes = True  # SQLAlchemyモデルからの変換を有効化

        # JSON Schema用のサンプルデータ
        json_schema_extra = {
            "example": {"id": 1, "name": "user", "email": "user@example.com"}
        }
