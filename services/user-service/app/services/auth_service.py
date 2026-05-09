from sqlalchemy.orm import Session
from app.core.security import create_access_token, hash_password, verify_password
from app.repos.user_repos import UserRepository
from app.models.user import User


class AuthService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def _ensure_role(self, role_name: str):
        role = self.repo.get_role_by_name(role_name)
        if not role:
            role = self.repo.create_role(role_name)
        return role

    def register(self, username: str, password: str) -> User:
        if self.repo.get_by_username(username):
            raise ValueError("Username already exists")

        password_hash = hash_password(password)
        user_role = self._ensure_role("user")
        return self.repo.create(username=username, password_hash=password_hash, role_id=user_role.id)

    def login(self, username: str, password: str) -> str:
        user = self.repo.get_by_username(username)
        if not user or not verify_password(password, user.password_hash):
            raise ValueError("Invalid username or password")

        token = create_access_token()
        self.repo.create_token(user.id, token)
        return token

    def get_user_by_token(self, token: str) -> User | None:
        return self.repo.get_user_by_token(token)

    def make_admin(self, user_id: int) -> None:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        admin_role = self._ensure_role("admin")
        user.role = admin_role
        self.repo.db.commit()

    def ensure_roles_exist(self) -> None:
        self._ensure_role("user")
        self._ensure_role("admin")

    def has_admin_user(self) -> bool:
        users = self.repo.get_users_by_role_name("admin")
        return len(users) > 0

    def create_admin_user(self, username: str, password: str) -> User:
        if self.repo.get_by_username(username):
            user = self.repo.get_by_username(username)
            if user.role_name != "admin":
                admin_role = self._ensure_role("admin")
                user.role = admin_role
                self.repo.db.commit()
            return user

        password_hash = hash_password(password)
        admin_role = self._ensure_role("admin")
        return self.repo.create(username=username, password_hash=password_hash, role_id=admin_role.id)
