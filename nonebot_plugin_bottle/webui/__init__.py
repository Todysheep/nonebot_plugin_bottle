from nonebot import get_driver, get_app
from nonebot import logger
from .api import router

@get_driver().on_startup
def _():
    try:
        get_app().include_router(router)
    except Exception as e:
        logger.error(f"bottleapi启动失败：{e}")