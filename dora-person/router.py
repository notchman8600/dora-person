# Standard Library
import os

# Third Party Library
import httpx
from controller import DoraController
from fastapi import Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.routing import APIRouter
from fastapi.security import OAuth2AuthorizationCodeBearer, OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from fastapi_login import LoginManager
from jwt import PyJWTError, decode, encode

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
        self.dora_router = APIRouter(prefix="/", tags=["dora"])
        self.templates = Jinja2Templates(directory="templates")
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
            return self.templates.TemplateResponse("index.html", {"request": request, "title": "Dora"})

        @self.dora_router.get("/login")
        def login(request: Request):
            github_oauth_url = f"https://github.com/login/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URL}"
            return RedirectResponse(url=github_oauth_url)

        @self.dora_router.get("/auth")
        async def auth(code: str = "", request: Request = Depends()):
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

            token = encode({"github_id": user["id"]}, SECRET_KEY, algorithm="HS256")
            return {"token": token}

        @self.dora_router.get("/vote")
        async def vote_page(request: Request, token: str = Depends(oauth2_scheme)):
            try:
                payload = decode(token, SECRET_KEY, algorithms=["HS256"])
                github_id = payload.get("github_id")
            except PyJWTError:
                raise HTTPException(status_code=401, detail="Unauthorized")
            return self.templates.TemplateResponse("vote.jinja2.html", {"request": request, "github_id": github_id})

        @self.dora_router.post("/vote/{target_user_id}")
        async def store_access_count(user: dict[str, str] = Depends(self.get_current_user), target_user_id: str = ""):
            self.dora_controller.count_store(user.get("user_id", "example-user-id"), target_user_id)

        return True

    def get_instance(self) -> APIRouter:
        return self.dora_router
