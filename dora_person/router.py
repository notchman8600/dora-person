# Standard Library
import datetime
import os

# Third Party Library
import httpx
from fastapi import Depends, Form, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from fastapi.routing import APIRouter
from fastapi.security import OAuth2AuthorizationCodeBearer, OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from fastapi_login import LoginManager
from jwt import PyJWTError, decode, encode

# First Party Library
from dora_person.controller import DoraController
from dora_person.request import SubmitDoraPersonRequestDto

oauth_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://github.com/login/oauth/authorize",
    tokenUrl="https://github.com/login/oauth/access_token",
    refreshUrl="https://github.com/login/oauth/access_token",
    scopes={"user:email": "Read user email"},
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


CLIENT_ID = os.getenv("CLIENT_ID")  # Set your GitHub App's Client ID here
CLIENT_SECRET = os.getenv("CLIENT_SECRET")  # Set your GitHub App's Client Secret here
REDIRECT_URL = os.getenv("REDIRECT_URL")  # Set your redirect URL here
SECRET_KEY = os.environ.get("SECRET_KEY", "NOTCH_MAN_IS_GOD")
ALGORITHM = "HS256"
MOCK_USER_ID = "mock_user_id"


class DoraRouter:
    dora_router: APIRouter
    dora_controller: DoraController
    templates: Jinja2Templates
    manager: LoginManager

    def __init__(self, templates: Jinja2Templates, dora_controller: DoraController) -> None:
        self.dora_router = APIRouter(prefix="", tags=["dora"])
        self.templates = templates
        self.dora_controller = dora_controller
        self.__init_route()

    async def get_current_user(self, token: str = Depends(oauth2_scheme)) -> dict[str, str]:
        credentials_exception = HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("github_id")
            if user_id is None:
                raise credentials_exception
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access token is expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except PyJWTError:
            raise credentials_exception
        if os.getenv("DEVELOPMENT"):
            return {"user_id": MOCK_USER_ID}
        return {"user_id": user_id}

    def __init_route(self) -> bool:
        # トップページ
        @self.dora_router.get("/")
        async def render_index_page(request: Request):
            return self.templates.TemplateResponse("index.jinja2.html", {"request": request, "title": "Dora"})

        @self.dora_router.get("/login")
        def login(request: Request):
            github_oauth_url = f"https://github.com/login/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URL}"
            return RedirectResponse(url=github_oauth_url)

        @self.dora_router.get("/auth")
        async def auth(request: Request, code: str = ""):
            if code == "":
                raise HTTPException(status_code=401, detail="Unauthorized")
            data = {"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "code": code}
            headers = {"Accept": "application/json"}
            async with httpx.AsyncClient() as client:
                r = await client.post("https://github.com/login/oauth/access_token", data=data, headers=headers)
                rj = r.json()
                if "error" in rj:
                    raise HTTPException(status_code=400, detail=rj["error"])
                access_token = rj["access_token"]
            user = await self.dora_controller.get_user_detail(access_token)
            expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
            token = encode(
                {"github_id": user.user_id, "avatar_url": user.avatar_url, "github_name": user.user_name, "exp": expire},
                SECRET_KEY,
                algorithm="HS256",
            )
            response = self.templates.TemplateResponse("auth.jinja2.html", {"request": request})
            response.set_cookie(key="access_token", value=f"Bearer {token}")
            return response

        @self.dora_router.get("/vote")
        async def vote_page(request: Request):
            try:
                token_str = request.cookies.get("access_token")
                if token_str is None:
                    raise HTTPException(status_code=400, detail="Bad Request")

                split_cookie = token_str.split(" ")
                if len(split_cookie) != 2:
                    raise HTTPException(status_code=401, detail="Unauthorized")
                token = split_cookie[1]
                payload = decode(token, SECRET_KEY, algorithms=["HS256"])
                name = payload.get("github_name")
                dora_persons = self.dora_controller.get_dora_person_candidates()

            except PyJWTError:
                raise HTTPException(status_code=401, detail="Unauthorized")

            return self.templates.TemplateResponse(
                "vote.jinja2.html", {"request": request, "github_id": name, "dora_persons": dora_persons}
            )

        @self.dora_router.post("/submit")
        async def submit_dora_person(request: Request, response: Response, message: str = Form(...)):
            try:
                token_str = request.cookies.get("access_token")
                if token_str is None:
                    raise HTTPException(status_code=400, detail="Bad Request")

                split_cookie = token_str.split(" ")
                if len(split_cookie) != 2:
                    raise HTTPException(status_code=401, detail="Unauthorized")
                token = split_cookie[1]
                payload = decode(token, SECRET_KEY, algorithms=["HS256"])
                github_id: str = payload.get("github_name")
                avatar_url: str = payload.get("avatar_url")
            except PyJWTError:
                raise HTTPException(status_code=401, detail="Unauthorized")
            request_dto = SubmitDoraPersonRequestDto(name=github_id, message=message, avatar_url=avatar_url)
            err = self.dora_controller.submit_dora_person(request_dto)
            if err is not None:
                raise HTTPException(status_code=500, detail="Internal Server Error")
            return RedirectResponse(url="/vote", status_code=303)

        @self.dora_router.post("/vote")
        async def store_access_count(request: Request, target_user_id: str = Form(...)):
            try:
                token_str = request.cookies.get("access_token")
                if token_str is None:
                    raise HTTPException(status_code=400, detail="Bad Request")
                split_cookie = token_str.split(" ")
                if len(split_cookie) != 2:
                    raise HTTPException(status_code=401, detail="Unauthorized")
                token = split_cookie[1]
                payload = decode(token, SECRET_KEY, algorithms=["HS256"])
                github_id: str = payload.get("github_name")
            except PyJWTError:
                raise HTTPException(status_code=401, detail="Unauthorized")

            err = self.dora_controller.store_vote_count(github_id, target_user_id)
            if err is not None:
                raise HTTPException(status_code=500, detail="Internal Server Error")
            return RedirectResponse(url="/vote", status_code=303)

        @self.dora_router.get("/reset")
        async def store_access_count(request: Request):
            try:
                token_str = request.cookies.get("access_token")
                if token_str is None:
                    raise HTTPException(status_code=400, detail="Bad Request")
                split_cookie = token_str.split(" ")
                if len(split_cookie) != 2:
                    raise HTTPException(status_code=401, detail="Unauthorized")
                token = split_cookie[1]
                payload = decode(token, SECRET_KEY, algorithms=["HS256"])
                github_id: str = payload.get("github_name")
                if github_id == "notchman8600":
                    raise HTTPException(status_code=403, detail="君にその権限はない")
            except PyJWTError:
                raise HTTPException(status_code=401, detail="Unauthorized")

            err = self.dora_controller.reset_count()
            if err is not None:
                raise HTTPException(status_code=500, detail="Internal Server Error")
            return RedirectResponse(url="/vote", status_code=303)

    def get_instance(self) -> APIRouter:
        return self.dora_router
