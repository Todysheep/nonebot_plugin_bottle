from nonebot import get_driver
from pydantic import Extra, BaseModel


class Config(BaseModel, extra=Extra.ignore):
    # 百度智能云文字审核API
    # 申请网址：https://cloud.baidu.com/doc/ANTIPORN/s/dkk6wyt3z
    nonebot_plugin_bottle_api_key: str = ""
    nonebot_plugin_bottle_secret_key: str = ""
    # 是否将图片保存在本地
    nonebot_plugin_bottle_local_storage: bool = True
    # 瓶子最大字符数量
    nonebot_plugin_bottle_max_length: int = 0
    # 最大换行数量
    nonebot_plugin_bottle_max_return: int = 0
    # 字符与换行的比率
    nonebot_plugin_bottle_rt_rate: int = 0


config = Config.parse_obj(get_driver().config.dict())
api_key = config.nonebot_plugin_bottle_api_key
secret_key = config.nonebot_plugin_bottle_secret_key
local_storage = config.nonebot_plugin_bottle_local_storage
maxlen = config.nonebot_plugin_bottle_max_length
maxrt = config.nonebot_plugin_bottle_max_return
rtrate = config.nonebot_plugin_bottle_rt_rate
