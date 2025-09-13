"""ユーザー関連のAPIエンドポイント

PostgreSQLを使用したユーザー管理のためのREST APIエンドポイントです。
ユーザー情報、認証情報などの構造化データを管理します。
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from config import get_db
from schemas.users import UserCreate, UserResponse, UserUpdate
from services.users import UserService

# ユーザー管理用ルーター
router = APIRouter(
    prefix="/api/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="ユーザー登録",
    description="新しいユーザーを登録します。パスワードは自動的にハッシュ化されます。",
    response_description="作成されたユーザー情報",
)
async def create_user(
    user_data: UserCreate,  # リクエストボディ（Pydanticで自動バリデーション）
    db: Session = Depends(get_db),  # データベースセッション（依存性注入）
) -> UserResponse:
    """ユーザーを作成する

    Args:
        user_data: ユーザー作成データ（自動的にバリデーション済み）
        db: データベースセッション（依存性注入）

    Returns:
        UserResponse: 作成されたユーザー情報

    Raises:
        HTTPException: ユーザー名またはメールアドレスが重複している場合（400）
    """

    # 1. ユーザー名の重複チェック
    if UserService.is_name_taken(db, user_data.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"ユーザー名 '{user_data.name}' は既に使用されています",
        )

    # 2. メールアドレスの重複チェック
    if UserService.is_email_taken(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"メールアドレス '{user_data.email}' は既に使用されています",
        )

    # 3. ユーザー作成
    try:
        db_user = UserService.create_user(db, user_data)
        return UserResponse.model_validate(db_user)
    except IntegrityError:
        # データベースレベルでの制約違反（念のため）
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ユーザー名またはメールアドレスが既に使用されています",
        )


@router.get(
    "/",
    response_model=List[UserResponse],
    summary="ユーザー一覧取得",
    description="すべてのユーザーを取得します。",
    response_description="ユーザー一覧",
)
async def get_users(db: Session = Depends(get_db)) -> List[UserResponse]:
    """すべてのユーザーを取得する

    Args:
        db: データベースセッション（依存性注入）

    Returns:
        List[UserResponse]: ユーザー一覧
    """
    users = UserService.get_all_users(db)
    return [UserResponse.model_validate(user) for user in users]


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="ユーザー詳細取得",
    description="指定されたIDのユーザーを取得します。",
    response_description="ユーザー詳細",
)
async def get_user(user_id: int, db: Session = Depends(get_db)) -> UserResponse:
    """指定されたIDのユーザーを取得する

    Args:
        user_id: ユーザーID
        db: データベースセッション（依存性注入）

    Returns:
        UserResponse: ユーザー詳細

    Raises:
        HTTPException: ユーザーが存在しない場合（404）
    """
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {user_id} のユーザーが見つかりません",
        )
    return UserResponse.model_validate(user)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="ユーザー更新",
    description="指定されたIDのユーザー情報を更新します。名前・メールアドレスとパスワードの両方を更新可能です。",
    response_description="更新されたユーザー情報",
)
async def update_user(
    user_id: int,  # パスパラメータ
    user_data: UserUpdate,  # リクエストボディ
    db: Session = Depends(get_db),  # データベースセッション（依存性注入）
) -> UserResponse:
    """ユーザー情報を更新する

    Args:
        user_id: ユーザーID
        user_data: 更新データ（自動的にバリデーション済み）
        db: データベースセッション（依存性注入）

    Returns:
        UserResponse: 更新されたユーザー情報

    Raises:
        HTTPException: ユーザーが存在しない場合（404）
        HTTPException: パスワード変更時に現在のパスワードが正しくない場合（400）
        HTTPException: ユーザー名またはメールアドレスが重複している場合（400）
    """

    try:
        updated_user = UserService.update_user(db, user_id, user_data)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ID {user_id} のユーザーが見つかりません",
            )

        return UserResponse.model_validate(updated_user)

    except ValueError as e:
        # パスワード関連のエラー
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except IntegrityError:
        # データベース制約違反（重複エラー）
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ユーザー名またはメールアドレスが既に使用されています",
        )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="ユーザー削除",
    description="指定されたIDのユーザーを削除します。",
)
async def delete_user(user_id: int, db: Session = Depends(get_db)) -> None:
    """指定されたIDのユーザーを削除する

    Args:
        user_id: ユーザーID
        db: データベースセッション（依存性注入）

    Raises:
        HTTPException: ユーザーが存在しない場合（404）
    """
    if not UserService.delete_user(db, user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {user_id} のユーザーが見つかりません",
        )
