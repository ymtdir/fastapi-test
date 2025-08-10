"""認証サービス

JWT認証とログイン機能を処理します。
"""

from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from fastapi import HTTPException, status, Header
from models.user import User
from schemas.auth import UserLogin, TokenData
from .users import UserService
from config import settings

# JWT設定
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


class AuthService:
    """認証サービスクラス

    JWT認証とログイン機能の実装を担当。
    """

    @staticmethod
    def get_token_from_header(
        authorization: Optional[str] = Header(None),
    ) -> Optional[str]:
        """Authorizationヘッダーからトークンを取得する

        Args:
            authorization: Authorizationヘッダーの値

        Returns:
            Optional[str]: トークン（Bearer プレフィックスを除いたもの）
        """
        if not authorization:
            return None

        if not authorization.startswith("Bearer "):
            return None

        return authorization.replace("Bearer ", "")

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """ユーザー認証を行う

        Args:
            db: データベースセッション
            email: メールアドレス
            password: パスワード

        Returns:
            Optional[User]: 認証成功時はユーザーオブジェクト、失敗時はNone
        """
        # メールアドレスでユーザーを取得
        user = UserService.get_user_by_email(db, email)
        if not user:
            return None

        # パスワードを検証
        if not UserService.verify_password(password, user.password):
            return None

        return user

    @staticmethod
    def create_access_token(
        data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        """アクセストークンを作成する

        Args:
            data: トークンに含めるデータ
            expires_delta: 有効期限（指定しない場合はデフォルト値を使用）

        Returns:
            str: JWTアクセストークン
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Optional[TokenData]:
        """トークンを検証する

        Args:
            token: JWTトークン

        Returns:
            Optional[TokenData]: 検証成功時はトークンデータ、失敗時はNone
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                return None
            token_data = TokenData(email=email)
            return token_data
        except JWTError:
            return None

    @staticmethod
    def login_user(db: Session, user_login: UserLogin) -> dict:
        """ユーザーログインを処理する

        Args:
            db: データベースセッション
            user_login: ログインデータ

        Returns:
            dict: アクセストークンとトークンタイプを含む辞書

        Raises:
            HTTPException: 認証失敗時
        """
        # ユーザー認証
        user = AuthService.authenticate_user(db, user_login.email, user_login.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="メールアドレスまたはパスワードが正しくありません",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # アクセストークンを作成
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = AuthService.create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {"id": user.id, "name": user.name, "email": user.email},
        }
