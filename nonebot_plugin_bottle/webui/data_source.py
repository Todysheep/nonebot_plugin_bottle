from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession
from .template import getHtml

from ..model import Bottle

from .model.bottle_resp import Comment as CommentResp, Bottle as BottleResp

from ..data_source import bottle_manager

async def bottle_model_to_resp(bottle: Bottle, session: AsyncSession) -> BottleResp:
    bottleResp = BottleResp(id = bottle.id, user_id=bottle.user_id, group_id=bottle.group_id, user_name=bottle.user_name,
                                    group_name=bottle.group_name,content=getHtml(bottle.content), report=bottle.report,like=bottle.like,picked=bottle.picked,time=bottle.time.strftime("%Y-%m-%d, %H:%M:%S"), comment=[])
    comments = await bottle_manager.get_comment(bottle=bottle, session=session, limit=3)
    for comment in comments:
        bottleResp.comment.append(CommentResp(id=comment.id,user_id=comment.user_id, user_name=comment.user_name, content=comment.content, time = comment.time.strftime("%Y-%m-%d, %H:%M:%S")))
    return bottleResp


async def get_bottles_resp(page: int, size: int, bottle_id: Optional[str], group_id: Optional[str], user_id: Optional[str], content: Optional[str], session: AsyncSession) -> List[BottleResp]:
        statement = select(Bottle).where(Bottle.is_del == False)
        if bottle_id:
            statement = statement.where(Bottle.id == int(bottle_id))
        if group_id:
            statement = statement.where(Bottle.group_id == int(group_id))
        if user_id:
            statement = statement.where(Bottle.user_id == int(user_id))
        if content:
            statement = statement.filter(Bottle.content.ilike(f"%{content}%"))
        statement = statement.order_by(Bottle.id).limit(size).offset((page - 1) * size)
        bottles = await session.scalars(
                statement=statement
            )
        resp = []
        for bottle in bottles:
            resp.append(await bottle_model_to_resp(bottle=bottle, session=session))
        return resp

async def get_comments(bottle_id: int, session: AsyncSession) -> List[CommentResp]:
    resp = []
    comments = await bottle_manager.get_comment_by_id(bottle_id=bottle_id, session=session, limit=3)
    for comment in comments:
         resp.append(CommentResp(id=comment.id,user_id=comment.user_id, user_name=comment.user_name,content=comment.content, time=comment.time.strftime("%Y-%m-%d, %H:%M:%S")))
    return resp
