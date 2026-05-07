from sqlalchemy.orm import Session
from app.models.user import User
from app.models.token import Token


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, username: str, password_hash: str) -> User:
        user = User(username=username, password_hash=password_hash)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_username(self, username: str) -> User | None:
        return self.db.query(User).filter(User.username == username).first()

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def create_token(self, user_id: int, token: str) -> Token:
        token_obj = Token(token=token, user_id=user_id)
        self.db.add(token_obj)
        self.db.commit()
        self.db.refresh(token_obj)
        return token_obj

    def get_user_by_token(self, token: str) -> User | None:
        token_obj = self.db.query(Token).filter(Token.token == token).first()
        return token_obj.user if token_obj else None

    def revoke_token(self, token: str) -> None:
        token_obj = self.db.query(Token).filter(Token.token == token).first()
        if token_obj:
            self.db.delete(token_obj)
            self.db.commit()
