from sqlalchemy.orm import Session
from app.core.security import create_access_token, hash_password, verify_password
from app.repos.user_repos import UserRepository
from app.models.user import User


class AuthService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def register(self, username: str, password: str) -> User:
        if self.repo.get_by_username(username):
            raise ValueError("Username already exists")

        password_hash = hash_password(password)
        return self.repo.create(username=username, password_hash=password_hash)

    def login(self, username: str, password: str) -> str:
        user = self.repo.get_by_username(username)
        if not user or not verify_password(password, user.password_hash):
            raise ValueError("Invalid username or password")

        token = create_access_token()
        self.repo.create_token(user.id, token)
        return token

    def get_user_by_token(self, token: str) -> User | None:
        return self.repo.get_user_by_token(token)
