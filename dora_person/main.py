"""Application entry point: builds and configures the FastAPI app."""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from dora_person.routers import pages, votes
from dora_person.templating import templates


def create_app() -> FastAPI:
    app = FastAPI()
    app.mount("/static", StaticFiles(directory="dora_person/static"), name="static")

    @app.exception_handler(Exception)
    async def universal_exception_handler(request: Request, exc: Exception):
        # TODO: 本当はここでロギングを行なう
        return templates.TemplateResponse(
            request,
            "error.jinja2.html",
            {"status_code": 500, "detail": f"An unexpected error occurred: {exc}"},
            status_code=500,
        )

    @app.exception_handler(HTTPException)
    async def custom_http_exception_handler(request: Request, exc: HTTPException):
        # TODO: 本当はここでロギングを行なう
        # 認証エラー時はログインページへリダイレクト
        if exc.status_code == status.HTTP_401_UNAUTHORIZED:
            return RedirectResponse(url="/login")
        return templates.TemplateResponse(
            request, "error.jinja2.html", {"status_code": 500, "detail": exc.detail}, status_code=500
        )

    app.include_router(pages.router)
    app.include_router(votes.router)
    return app


app = create_app()
