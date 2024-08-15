from fastapi.routing import APIRouter
from .utils import generate_password
from nonebot.log import logger
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, UTC
from pydantic import BaseModel
from .model.bottle_resp import Bottle
from ..data_source import bottle_manager
from nonebot_plugin_datastore import get_session
from sqlalchemy.ext.asyncio.session import AsyncSession

SECRET_KEY = "P8S8enUyywx8YEP39@o#DP@gRSQ9!ToZPFp#R#V%cya$!aNpNDrj!AT!a"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")

from ..config import config

router = APIRouter(prefix="/bottle/api", tags=["bottle-api"])

admin_user = config.nonebot_plugin_bottle_admin_user if config.nonebot_plugin_bottle_admin_user else ""
admin_password = config.nonebot_plugin_bottle_admin_password

class User(BaseModel):
    username: str
    password: str

print(config)

if not admin_password:
    admin_password = generate_password(12)
    logger.info(f"漂流瓶随机管理员密码已生成：{admin_password}")

user = User(username=admin_user, password=admin_password)

def verify_password(plain_password, password):
    return plain_password == password

def get_user(username: str):
    if username == admin_user:
        return user
    return None
    
def authenticate_user(username: str, password: str):
    user = get_user(username)
    print(user)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


class RefreshTokenRequest(BaseModel):
    refresh_token: str


@router.post("/refresh", response_model=dict)
async def refresh_access_token(request: RefreshTokenRequest):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(request.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("scope") != "refresh_token":
            raise credentials_exception
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(username=username)
    if user is None:
        raise credentials_exception

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"token": access_token, "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme)):
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
    except JWTError:
        raise credentials_exception
    user = get_user(username=username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    return current_user

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/token", response_model=dict)
async def login_for_access_token(form_data: LoginRequest):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"token": access_token, "token_type": "bearer"}

@router.get("/getBottles", response_model=list[Bottle])
async def get_bottles(page: int = 0, page_size: int = 10, session: AsyncSession = Depends(get_session), current_user: dict = Depends(get_current_active_user)):
    bottles = await bottle_manager.get_bottles_resp(page = page, size=page_size, session=session)
    
    return bottles