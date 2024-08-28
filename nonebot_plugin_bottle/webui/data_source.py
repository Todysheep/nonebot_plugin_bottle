from typing import List, Optional

from nonebot import require

require("nonebot_plugin_datastore")
from nonebot_plugin_datastore.db import get_engine
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio.session import AsyncSession
from .template import getHtml

from ..model import Bottle

from .model.bottle_resp import Comment as CommentResp, Bottle as BottleResp, ListBottleResp

from ..data_source import bottle_manager


async def bottle_model_to_resp(bottle: Bottle, session: AsyncSession) -> BottleResp:
    bottleResp = BottleResp(
        id=bottle.id,
        user_id=bottle.user_id,
        group_id=bottle.group_id,
        user_name=bottle.user_name,
        group_name=bottle.group_name,
        content=getHtml(bottle.content),
        report=bottle.report,
        like=bottle.like,
        picked=bottle.picked,
        time=bottle.time.strftime("%Y-%m-%d, %H:%M:%S"),
        comment=[],
    )
    comments = await bottle_manager.get_comment(bottle=bottle, session=session, limit=3)
    for comment in comments:
        bottleResp.comment.append(
            CommentResp(
                id=comment.id,
                user_id=comment.user_id,
                user_name=comment.user_name,
                content=comment.content,
                time=comment.time.strftime("%Y-%m-%d, %H:%M:%S"),
            )
        )
    return bottleResp


async def get_bottles_resp(
    page: int,
    size: int,
    bottle_id: Optional[str],
    group_id: Optional[str],
    user_id: Optional[str],
    content: Optional[str],
    session: AsyncSession,
) -> ListBottleResp:

    base_statement = select(Bottle).where(Bottle.is_del == False, Bottle.approved == True)
    if bottle_id:
        base_statement = base_statement.where(Bottle.id == int(bottle_id))
    if group_id:
        base_statement = base_statement.where(Bottle.group_id == int(group_id))
    if user_id:
        base_statement = base_statement.where(Bottle.user_id == int(user_id))
    if content:
        base_statement = base_statement.filter(Bottle.content.ilike(f"%{content}%"))

    # 获取总数
    total_statement = select(func.count()).select_from(base_statement.subquery())
    total_count = await session.scalar(total_statement)

    # 获取分页数据
    statement = base_statement.order_by(Bottle.id).limit(size).offset(page * size)
    bottles = await session.scalars(statement=statement)

    resp = []
    for bottle in bottles:
        resp.append(await bottle_model_to_resp(bottle=bottle, session=session))

    return ListBottleResp(bottles=resp, total = total_count)


async def get_comments(bottle_id: int, session: AsyncSession) -> List[CommentResp]:
    resp = []
    comments = await bottle_manager.get_comment_by_id(
        bottle_id=bottle_id, session=session, limit=3
    )
    for comment in comments:
        resp.append(
            CommentResp(
                id=comment.id,
                user_id=comment.user_id,
                user_name=comment.user_name,
                content=comment.content,
                time=comment.time.strftime("%Y-%m-%d, %H:%M:%S"),
            )
        )
    return resp


async def get_unapproved_bottles_resp(
    page: int, size: int, session: AsyncSession
) -> ListBottleResp:
    base_statement = (
        select(Bottle).where(Bottle.is_del == False).where(Bottle.approved == False)
    )
    # 获取总数
    total_statement = select(func.count()).select_from(base_statement.subquery())
    total_count = await session.scalar(total_statement)

    # 获取分页数据
    statement = base_statement.order_by(Bottle.id).limit(size).offset(page * size)
    bottles = await session.scalars(statement=statement)
    resp = []
    for bottle in bottles:
        resp.append(await bottle_model_to_resp(bottle=bottle, session=session))
    return ListBottleResp(bottles=resp, total = total_count)


async def approve_func(
    bottle_id: int, is_approved: bool, session: AsyncSession
) -> bool:
    statement = (
        select(Bottle)
        .where(Bottle.is_del == False)
        .where(Bottle.approved == False)
        .where(Bottle.id == bottle_id)
    )
    bottle = await session.scalar(statement=statement)
    print(bottle)
    if not bottle:
        return False
    if is_approved:
        bottle.approved = True
    else:
        bottle.is_del = True
    await session.commit()
    return True


from .model.resp import EachDay, Statistic


def get_date_format_function():
    engine = get_engine()
    # Check the database dialect
    if "postgresql" in engine.dialect.name:
        return func.to_char(Bottle.time, "YYYY-MM-DD")
    elif "mysql" in engine.dialect.name:
        return func.date_format(Bottle.time, "%Y-%m-%d")
    elif "sqlite" in engine.dialect.name:
        return func.strftime("%Y-%m-%d", Bottle.time)
    else:
        raise NotImplementedError("Unsupported database dialect")


async def get_bottle_statistic(session: AsyncSession) -> Statistic:
    from datetime import datetime
    from datetime import timedelta

    last_7_days = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=6)
    daily_stats = await session.execute(
        select(
            get_date_format_function().label("date"),
            func.count(Bottle.id).label("count"),
        )
        .where(Bottle.time >= last_7_days)
        .group_by("date")
        .order_by("date")
    )
    aggregated_data = {row.date: row.count for row in daily_stats}
    dates = [(last_7_days + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

    result = Statistic(
        days=[EachDay(date=date, count=aggregated_data.get(date, 0)) for date in dates],
        total=await session.scalar(func.count(Bottle.id)),
        unapproved=await session.scalar(
            select(func.count(Bottle.id)).where(
                Bottle.is_del == False, Bottle.approved == False
            )
        ),
        deleted=await session.scalar(
            select(func.count(Bottle.id)).where(Bottle.is_del == True)
        ),
        avl=await session.scalar(
            select(func.count(Bottle.id)).where(
                Bottle.is_del == False, Bottle.approved == True
            )
        ),
    )

    return result
