from pydantic import BaseModel, Extra
from nonebot import get_driver


class Config(BaseModel, extra=Extra.ignore):
    # 百度智能云文字审核API
    # 申请网址：https://cloud.baidu.com/doc/ANTIPORN/s/dkk6wyt3z
    nonebot_plugin_bottle_api_key: str = ""
    nonebot_plugin_bottle_secret_key: str = ""


config = Config.parse_obj(get_driver().config.dict())
api_key = config.nonebot_plugin_bottle_api_key
secret_key = config.nonebot_plugin_bottle_secret_key
