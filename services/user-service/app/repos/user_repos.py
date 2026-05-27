from sqlalchemy.orm import Session
from app.models.user import User
from app.models.token import Token
from app.models.role import Role


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, username: str, password_hash: str, role_id: int) -> User:
        user = User(username=username, password_hash=password_hash, role_id=role_id)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_username(self, username: str) -> User | None:
        return self.db.query(User).filter(User.username == username).first()

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_role_by_name(self, name: str) -> Role | None:
        return self.db.query(Role).filter(Role.name == name).first()

    def create_role(self, name: str) -> Role:
        role = Role(name=name)
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return role

    def get_users_by_role_name(self, role_name: str):
        return self.db.query(User).join(Role).filter(Role.name == role_name).all()

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
