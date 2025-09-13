"""ユーザーサービス

ユーザー関連のビジネスロジックを処理します。
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
from models.user import User
from schemas.users import UserCreate, UserUpdate

# パスワードハッシュ化用の設定
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """ユーザーサービスクラス

    データベース操作とビジネスルールの実装を担当。
    """

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """ユーザーを作成する

        Args:
            db: データベースセッション
            user_data: ユーザー作成データ

        Returns:
            User: 作成されたユーザーオブジェクト

        Raises:
            IntegrityError: ユーザー名またはメールアドレスが重複している場合
        """
        # パスワードをハッシュ化
        hashed_password = pwd_context.hash(user_data.password)

        # SQLAlchemyモデルインスタンスの作成
        db_user = User(
            name=user_data.name, email=user_data.email, password=hashed_password
        )

        try:
            # データベースに追加
            db.add(db_user)
            db.commit()
            db.refresh(db_user)  # 自動生成されたIDなどを取得
            return db_user
        except IntegrityError:
            db.rollback()
            raise

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """IDでユーザーを取得する

        Args:
            db: データベースセッション
            user_id: ユーザーID

        Returns:
            Optional[User]: ユーザーオブジェクト（存在しない場合はNone）
        """
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_name(db: Session, name: str) -> Optional[User]:
        """ユーザー名でユーザーを取得する

        Args:
            db: データベースセッション
            name: ユーザー名

        Returns:
            Optional[User]: ユーザーオブジェクト（存在しない場合はNone）
        """
        return db.query(User).filter(User.name == name).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """メールアドレスでユーザーを取得する

        Args:
            db: データベースセッション
            email: メールアドレス

        Returns:
            Optional[User]: ユーザーオブジェクト（存在しない場合はNone）
        """
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def is_name_taken(db: Session, name: str) -> bool:
        """ユーザー名が既に使用されているかチェックする

        Args:
            db: データベースセッション
            name: チェックするユーザー名

        Returns:
            bool: 使用済みの場合True、利用可能な場合False
        """
        return UserService.get_user_by_name(db, name) is not None

    @staticmethod
    def is_email_taken(db: Session, email: str) -> bool:
        """メールアドレスが既に使用されているかチェックする

        Args:
            db: データベースセッション
            email: チェックするメールアドレス

        Returns:
            bool: 使用済みの場合True、利用可能な場合False
        """
        return UserService.get_user_by_email(db, email) is not None

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """パスワードを検証する

        Args:
            plain_password: 平文パスワード
            hashed_password: ハッシュ化済みパスワード

        Returns:
            bool: パスワードが一致する場合True
        """
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_all_users(db: Session) -> List[User]:
        """すべてのユーザーを取得する

        Args:
            db: データベースセッション

        Returns:
            List[User]: ユーザーリスト
        """
        return db.query(User).all()

    @staticmethod
    def update_user(db: Session, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """ユーザー情報を更新する

        Args:
            db: データベースセッション
            user_id: ユーザーID
            user_data: 更新データ

        Returns:
            Optional[User]: 更新されたユーザーオブジェクト（存在しない場合はNone）

        Raises:
            IntegrityError: ユーザー名またはメールアドレスが重複している場合
            ValueError: パスワード変更時に現在のパスワードが正しくない場合
        """
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            return None

        # 更新データがある場合のみ更新
        update_data = user_data.model_dump(exclude_unset=True)

        # パスワード変更の処理
        if "new_password" in update_data:
            # 新しいパスワードが指定されている場合、現在のパスワードが必要
            if "current_password" not in update_data:
                raise ValueError("パスワードを変更する場合は現在のパスワードが必要です")

            # 現在のパスワードを検証
            if not UserService.verify_password(
                update_data["current_password"], db_user.password
            ):
                raise ValueError("現在のパスワードが正しくありません")

            # 新しいパスワードをハッシュ化
            update_data["password"] = pwd_context.hash(update_data["new_password"])

            # パスワード関連のフィールドを削除
            update_data.pop("current_password", None)
            update_data.pop("new_password", None)

        try:
            for field, value in update_data.items():
                setattr(db_user, field, value)

            db.commit()
            db.refresh(db_user)
            return db_user
        except IntegrityError:
            db.rollback()
            raise

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """ユーザーを削除する

        Args:
            db: データベースセッション
            user_id: ユーザーID

        Returns:
            bool: 削除成功の場合True、ユーザーが存在しない場合False
        """
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            return False

        db.delete(db_user)
        db.commit()
        return True
