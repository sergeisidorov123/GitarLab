from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.auth import UserRegister, UserLogin, AuthResponse
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
http_bearer = HTTPBearer(auto_error=False)


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


@router.post("/register", response_model=UserResponse)
def register(user_data: UserRegister, service: AuthService = Depends(get_auth_service)):
    try:
        user = service.register(user_data.username, user_data.password)
        return user
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/login", response_model=AuthResponse)
def login(credentials: UserLogin, service: AuthService = Depends(get_auth_service)):
    try:
        token = service.login(credentials.username, credentials.password)
        return AuthResponse(access_token=token, username=credentials.username)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = AuthService(db).get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user


def get_current_user_optional(credentials = Depends(http_bearer), db: Session = Depends(get_db)):
    if not credentials:
        return None
    user = AuthService(db).get_user_by_token(credentials.credentials)
    return user


@router.get("/me", response_model=UserResponse)
def get_me(current_user = Depends(get_current_user)):
    return current_user
