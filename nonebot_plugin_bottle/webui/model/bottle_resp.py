from pydantic import BaseModel
from typing import List

class Comment(BaseModel):
    id: int
    user_id: int
    user_name: str
    content: str
    time: str

class Bottle(BaseModel):
    id: int
    user_id: int
    group_id: int
    user_name: str
    group_name: str
    content: str
    report: str
    like: str
    picked: str
    time: str
    comment: List[Comment]

class ListBottleResp(BaseModel):
    bottles: List[Bottle]
    total: int