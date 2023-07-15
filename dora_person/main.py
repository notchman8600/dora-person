# Standard Library
import os

# Third Party Library
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# First Party Library
from dora_person.controller import DoraController
from dora_person.router import DoraRouter

SECRET = os.environ.get("SECRET_DORA", "I_LIKE_GASOLINE_VERY_WELL")
app = FastAPI()
# 静的ファイルのパスを指定する
app.mount(
    "/static",
    StaticFiles(directory="dora_person/static"),
    name="static",
)


# ルーターインスタンスの作成
dora_router = DoraRouter(DoraController())
# ルーターの登録
app.include_router(dora_router.get_instance())
