# Standard Library
import os

# Third Party Library
import httpx
from fastapi import Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.routing import APIRouter
from fastapi.security import OAuth2AuthorizationCodeBearer, OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from fastapi_login import LoginManager
from jwt import PyJWTError, decode, encode

# First Party Library
from dora_person.controller import DoraController

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
SECRET_KEY = os.environ.get("SECRET_KEY", "NOTCH_MAN_")
ALGORITHM = "HS256"
MOCK_USER_ID = "mock_user_id"


class DoraRouter:
    dora_router: APIRouter
    dora_controller: DoraController
    templates: Jinja2Templates
    manager: LoginManager

    def __init__(self, dora_controller: DoraController) -> None:
        self.dora_router = APIRouter(prefix="", tags=["dora"])
        self.templates = Jinja2Templates(directory="dora_person/templates")
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
        async def auth(request: Request, response: Response, code: str = ""):
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
                r = await client.get("https://api.github.com/user", headers={"Authorization": f"token {access_token}"})
            user = r.json()

            token = encode({"github_id": user["id"], "access_token": access_token}, SECRET_KEY, algorithm="HS256")
            response.set_cookie(key="access_token", value=f"Bearer {token}")
            return {"message": "authentication success"}

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
                github_id = payload.get("github_id")
                access_token = payload.get("access_token")
            except PyJWTError:
                raise HTTPException(status_code=401, detail="Unauthorized")
            user_data = await self.dora_controller.get_user_detail(github_id, access_token)
            return self.templates.TemplateResponse("vote.jinja2.html", {"request": request, "github_id": user_data.user_name})

        @self.dora_router.post("/vote/{target_user_id}")
        async def store_access_count(request: Request, target_user_id: str = ""):
            try:
                token = request.cookies.get("access_token")
                payload = decode(token, SECRET_KEY, algorithms=["HS256"])
                github_id = payload.get("github_id")
            except PyJWTError:
                raise HTTPException(status_code=401, detail="Unauthorized")

            self.dora_controller.count_store(github_id, target_user_id)

        return True

    def get_instance(self) -> APIRouter:
        return self.dora_router
