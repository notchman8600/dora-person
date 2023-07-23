# Standard Library
import os
from http.client import HTTPException

# Third Party Library
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

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

templates = Jinja2Templates(directory="dora_person/templates")


@app.exception_handler(Exception)
async def universal_exception_handler(request: Request, exc: Exception):
    # TODO: 本当はここでロギングを行なう
    return templates.TemplateResponse(
        "error.jinja2.html",
        {"request": request, "status_code": 500, "detail": f"An unexpected error occurred: {str(exc)}"},
        status_code=500,
    )


# HTTPException発生時のエラーページの表示
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    # TODO: 本当はここでロギングを行なう

    return templates.TemplateResponse(
        "error.jinja2.html", {"request": request, "status_code": 500, "detail": exc.args}, status_code=500
    )


# ルーターインスタンスの作成
dora_router = DoraRouter(templates=templates, dora_controller=DoraController())
# ルーターの登録
app.include_router(dora_router.get_instance())
