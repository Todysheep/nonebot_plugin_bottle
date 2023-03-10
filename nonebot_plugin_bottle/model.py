from datetime import datetime
from typing import List, Tuple, Optional

from nonebot.log import logger
from sqlalchemy.ext.mutable import MutableList
from nonebot_plugin_datastore import get_plugin_data
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy import (
    JSON,
    ARRAY,
    Index,
    Column,
    String,
    BigInteger,
    ForeignKey,
    UniqueConstraint,
    func,
    select,
)

Model = get_plugin_data().Model


class Comment(Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    user_name: Mapped[str]
    content: Mapped[str]
    time: Mapped[datetime] = mapped_column(default=datetime.now())

    bottle_id: Mapped[int]


class Report(Model):
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "bottle_id",
            name="unique_report",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger)

    bottle_id: Mapped[int]


class Bottle(Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    group_id: Mapped[int] = mapped_column(BigInteger)
    user_name: Mapped[str]
    group_name: Mapped[str]
    content: Mapped[str]
    report: Mapped[int] = mapped_column(default=0)
    picked: Mapped[int] = mapped_column(default=0)
    is_del: Mapped[bool] = mapped_column(default=False)
    time: Mapped[datetime] = mapped_column(default=datetime.now())


Index(None, Bottle.user_id, Bottle.group_id)
