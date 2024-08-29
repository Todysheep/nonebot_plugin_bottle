from nonebot import get_driver, get_app
from nonebot import logger
from .api import router
from pathlib import Path
from fastapi.staticfiles import StaticFiles
import os

class SinglePageApplication(StaticFiles):
    def __init__(self, directory: os.PathLike, index="index.html"):
        self.index = index
        super().__init__(directory=directory, packages=None, html=True, check_dir=True)

    def lookup_path(self, path: str) -> tuple[str, os.stat_result | None]:
        full_path, stat_res = super().lookup_path(path)
        if stat_res is None:
            return super().lookup_path(self.index)
        return (full_path, stat_res)

@get_driver().on_startup
def _():
    try:
        get_app().include_router(router)

        frontend = Path(__file__).parent / "dist"

        get_app().mount("/bottle", SinglePageApplication(directory=frontend), name="web")

        logger.info(f"漂流瓶管理页面：http://{get_driver().config.host}:{get_driver().config.port}/bottle")
        from .api import admin_password, admin_user
        logger.info(f"漂流瓶管理用户名：{admin_user}  密码：{admin_password}")

    except Exception as e:
        logger.error(f"bottleapi启动失败：{e}")