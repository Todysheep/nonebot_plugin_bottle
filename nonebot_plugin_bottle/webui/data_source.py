import re
import time
import asyncio
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence

import httpx
import aiofiles
from base64 import b64encode
from nonebot.log import logger
from pydantic import parse_obj_as
from sqlalchemy import func, text, select
from sqlalchemy.ext.asyncio.session import AsyncSession
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot_plugin_datastore.db import get_engine, post_db_init, create_session
from .template import getHtml

from ..model import Like, Bottle, Report, Comment
from ..config import api_key, secret_key, local_storage
from ..exception import NotSupportMessage

from .model.bottle_resp import Comment as CommentResp, Bottle as BottleResp

from ..data_source import bottle_manager

async def bottle_model_to_resp(bottle: Bottle, session: AsyncSession) -> BottleResp:
    bottleResp = BottleResp(id = bottle.id, user_id=bottle.user_id, group_id=bottle.group_id, user_name=bottle.user_name,
                                    group_name=bottle.group_name,content=getHtml(bottle.content), report=bottle.report,like=bottle.like,picked=bottle.picked,time=bottle.time.strftime("%Y-%m-%d, %H:%M:%S"), comment=[])
    comments = await bottle_manager.get_comment(bottle=bottle, session=session, limit=3)
    for comment in comments:
        bottleResp.comment.append(CommentResp(id=comment.id,user_id=comment.user_id, user_name=comment.user_name, content=comment.content, time = comment.time.strftime("%Y-%m-%d, %H:%M:%S")))
    return bottleResp


async def get_bottles_resp(page: int, size: int, session: AsyncSession) -> List[BottleResp]:
        bottles = await session.scalars(
                select(Bottle).where(Bottle.is_del == False).order_by(Bottle.id).limit(size).offset((page - 1) * size)
            )
        resp = []
        for bottle in bottles:
            resp.append(bottle_model_to_resp(bottle=bottle, session=session))
        return resp

async def get_comments(bottle_id: int, session: AsyncSession) -> List[CommentResp]:
    resp = []
    comments = await bottle_manager.get_comment_by_id(bottle_id=bottle_id, session=session, limit=3)
    for comment in comments:
         resp.append(CommentResp(id=comment.id,user_id=comment.user_id, user_name=comment.user_name,content=comment.content, time=comment.time.strftime("%Y-%m-%d, %H:%M:%S")))
    return resp

async def search(session:AsyncSession, bottle_id: Optional[int], group_id: Optional[int], user_id: Optional[int], content: Optional[str]) -> List[BottleResp]:
    if bottle_id is None and group_id is None and user_id is None and content is None:
        return None
    from ..model import Bottle
    from sqlalchemy import select
    resp = []
    statement = select(Bottle)
    if bottle_id:
        statement.where(Bottle.id == bottle_id)
    if group_id:
        statement.where(Bottle.group_id == group_id)
    if user_id:
        statement.where(Bottle.user_id == user_id)
    if content:
        statement.filter(Bottle.content.ilike(f"%{content}%"))
    bottles = await session.scalars(statement=statement)
    for bottle in bottles:
        resp.append(bottle_model_to_resp(bottle=bottle, session=session))
    return resp
