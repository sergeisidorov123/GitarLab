import base64
import hashlib
import hmac
import secrets
from app.config import settings


def hash_password(password: str) -> str:
    salt = settings.PASSWORD_SALT.encode('utf-8')
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 200_000)
    return base64.urlsafe_b64encode(hashed).decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    return hmac.compare_digest(hash_password(password), password_hash)


def create_access_token() -> str:
    return secrets.token_urlsafe(32)
