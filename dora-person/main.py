# Standard Library
import os
from controller import DoraController

# Third Party Library
from fastapi import FastAPI
from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi.staticfiles import StaticFiles
from fastapi_login import LoginManager
from router import DoraRouter
from starlette.responses import RedirectResponse

SECRET = os.environ.get("SECRET_DORA", "I_LIKE_GASOLINE_VERY_WELL")
app = FastAPI()
# 静的ファイルのパスを指定する
app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static",
)


# ルーターインスタンスの作成
dora_router = DoraRouter(DoraController())
# ルーターの登録
app.include_router(dora_router.get_instance())
