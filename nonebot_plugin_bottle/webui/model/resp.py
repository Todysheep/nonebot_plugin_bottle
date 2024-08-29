from pydantic import BaseModel
from typing import List

class EachDay(BaseModel):
    date: str
    count: int

class Statistic(BaseModel):
    total: int # 总数
    unapproved: int # 未审批
    avl: int # 有效数
    deleted: int # 已删除
    days: List[EachDay] # 各天数据
    