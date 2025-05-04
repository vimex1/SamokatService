from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from typing import Annotated
from passlib.context import CryptContext
import jwt
from jose import JWTError
from models import Users as DBUser
from database import get_db
from schemas import Token, TokenData, User

from sqlalchemy.orm import Session

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Работа с паролем
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)



# Получение пользователя из БД
def get_user_by_username(db: Session, username: str):
    return db.query(DBUser).filter(DBUser.username == username).first()

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user





# Получение пользователя по токену
async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)], 
        db: Session = Depends(get_db)
        ):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user = get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user



# Проверка активности
async def get_current_active_user(current_user: Annotated[DBUser, Depends(get_current_user)]):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user



# Проверка роли: admin = 1
async def admin_only(current_user: Annotated[DBUser, Depends(get_current_active_user)]):
    if current_user.role_id != 1:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user



# Проверка роли: manager = 2
async def manager_only(current_user: Annotated[DBUser, Depends(get_current_active_user)]):
    if current_user.role_id != 2:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user



# Авторизация
@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
    db: Session = Depends(get_db)
    ):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
              )
    
    access_token = create_access_token(data={
    "sub": user.username,
    "role": user.role_id
    })

    return {"access_token": access_token, "token_type": "bearer"}



# Примеры защищённых маршрутов
@router.get("/users/me", response_model=User)
async def read_users_me(current_user: Annotated[DBUser, Depends(get_current_active_user)]):
    return current_user

@router.get("/admin", response_model=User)
async def get_admin_data(current_user: Annotated[DBUser, Depends(admin_only)]):
    return current_user

@router.get("/manager", response_model=User)
async def get_manager_data(current_user: Annotated[DBUser, Depends(manager_only)]):
    return current_user


# Создание JWT токена
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta 
    else:
        expire = expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Проверка токена
def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        if username is None:
            raise HTTPException(status_code=403, detail="Token is invalid or expired")
        return payload
    except JWTError:
        raise HTTPException(status_code=403, detail="Token is invalid or expired")
    

@router.get("/verify-token/{token}")
async def verify_user_token(token: str):
    verify_token(token=token)
    return {"message": "Token is invalid"}