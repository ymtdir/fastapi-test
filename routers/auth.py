"""認証関連のルーター

ログイン・ログアウトなどの認証機能を提供します。
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config import get_db
from schemas.auth import UserLogin, Token
from services.auth import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=Token)
async def login(user_login: UserLogin, db: Session = Depends(get_db)):
    """ユーザーログイン

    Args:
        user_login: ログインデータ
        db: データベースセッション

    Returns:
        Token: アクセストークンとトークンタイプ

    Raises:
        HTTPException: 認証失敗時
    """
    try:
        result = AuthService.login_user(db, user_login)
        return Token(
            access_token=result["access_token"], token_type=result["token_type"]
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ログイン処理中にエラーが発生しました",
        )


@router.post("/logout")
async def logout():
    """ユーザーログアウト

    注意: JWTはステートレスなので、サーバー側での処理は不要です。
    クライアント側でトークンを削除してください。

    Returns:
        dict: ログアウト成功メッセージ
    """
    return {
        "message": "ログアウトしました。クライアント側でトークンを削除してください。"
    }
