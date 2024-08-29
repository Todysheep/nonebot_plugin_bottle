from fastapi.routing import APIRouter
from .utils import generate_password
from nonebot.log import logger
from typing import Optional
from nonebot import get_app
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, UTC
from pydantic import BaseModel
from .model.bottle_resp import Comment, ListBottleResp
from nonebot_plugin_datastore import get_session
from sqlalchemy.ext.asyncio.session import AsyncSession
from ..data_source import cache_dir

SECRET_KEY = "P8S8enUyywx8YEP39@o#DP@gRSQ9!ToZPFp#R#V%cya$!aNpNDrj!AT!a"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")

from ..config import config

router = APIRouter(prefix="/bottle/api", tags=["bottle-api"])

get_app().mount("/bottle/images", StaticFiles(directory=cache_dir), name="static")

admin_user = config.nonebot_plugin_bottle_admin_user if config.nonebot_plugin_bottle_admin_user else ""
admin_password = config.nonebot_plugin_bottle_admin_password

class User(BaseModel):
    username: str
    password: str

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
async def _(form_data: LoginRequest):
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

@router.get("/getBottles", response_model=ListBottleResp)
async def _(page: int = 0, page_size: int = 10, bottle_id: Optional[str] = None, group_id:Optional[str] = None, user_id:Optional[str] = None, content: Optional[str] = None,session: AsyncSession = Depends(get_session), current_user: dict = Depends(get_current_active_user)):
    from .data_source import get_bottles_resp
    
    return await get_bottles_resp(page=page, size=page_size,bottle_id=bottle_id,group_id=group_id,user_id=user_id, content=content,session=session)

@router.get("/getComments", response_model=list[Comment])
async def _(bottle_id: int, session: AsyncSession = Depends(get_session), current_user: dict = Depends(get_current_active_user)):
    from .data_source import get_comments
    
    return await get_comments(bottle_id=bottle_id, session= session)

@router.get("/getUnApprovedBottle", response_model=ListBottleResp)
async def _(page: int = 0, page_size: int = 10, session: AsyncSession = Depends(get_session), current_user: dict = Depends(get_current_active_user)):
    from .data_source import get_unapproved_bottles_resp
    
    return await get_unapproved_bottles_resp(page=page, size=page_size, session= session)

class ApproveRespModel(BaseModel):
    code: int
    msg: str

class ApproveReqModel(BaseModel):
    bottle_id: int

@router.post("/approve", response_model=ApproveRespModel)
async def _(req: ApproveReqModel, session: AsyncSession = Depends(get_session), current_user: dict = Depends(get_current_active_user)):
    from .data_source import approve_func

    if await approve_func(bottle_id=req.bottle_id, is_approved=True, session=session):
        return ApproveRespModel(code=0, msg="操作成功")
    return ApproveRespModel(code=-1, msg="操作失败")

@router.post("/reject", response_model=ApproveRespModel)
async def _(req: ApproveReqModel, session: AsyncSession = Depends(get_session), current_user: dict = Depends(get_current_active_user)):
    from .data_source import approve_func

    if await approve_func(bottle_id=req.bottle_id, is_approved=False, session=session):
        return ApproveRespModel(code=0, msg="操作成功")
    return ApproveRespModel(code=-1, msg="操作失败")

from .model.resp import Statistic

@router.get("/statistic", response_model=Statistic)
async def _(session: AsyncSession = Depends(get_session), current_user: dict = Depends(get_current_active_user)):
    from .data_source import get_bottle_statistic

    return await get_bottle_statistic(session=session)