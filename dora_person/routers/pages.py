"""Page routes: the landing page and the GitHub OAuth login flow."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from dora_person.config import Settings, get_settings
from dora_person.dependencies import get_current_user, get_github_gateway, get_vote_service
from dora_person.errors import GitHubOAuthError
from dora_person.security import create_access_token
from dora_person.services.github import GitHubGateway
from dora_person.services.votes import VoteService
from dora_person.templating import get_templates

router = APIRouter(tags=["dora"])


@router.get("/")
async def render_index_page(request: Request, templates: Jinja2Templates = Depends(get_templates)):
    return templates.TemplateResponse(request, "index.jinja2.html", {"title": "Dora"})


@router.get("/login")
def login(gateway: GitHubGateway = Depends(get_github_gateway)):
    return RedirectResponse(url=gateway.authorize_url())


@router.get("/auth")
async def auth(
    request: Request,
    code: str = "",
    gateway: GitHubGateway = Depends(get_github_gateway),
    settings: Settings = Depends(get_settings),
    templates: Jinja2Templates = Depends(get_templates),
):
    if code == "":
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        access_token = await gateway.exchange_code_for_token(code)
    except GitHubOAuthError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err

    profile = await gateway.fetch_profile(access_token)
    token = create_access_token(
        {"github_id": profile.user_id, "avatar_url": profile.avatar_url, "github_name": profile.user_name},
        settings,
    )
    response = templates.TemplateResponse(request, "auth.jinja2.html")
    response.set_cookie(key="access_token", value=f"Bearer {token}")
    return response


@router.get("/vote")
async def vote_page(
    request: Request,
    user: dict[str, Any] = Depends(get_current_user),
    service: VoteService = Depends(get_vote_service),
    templates: Jinja2Templates = Depends(get_templates),
):
    candidates = service.list_candidates()
    return templates.TemplateResponse(
        request,
        "vote.jinja2.html",
        {"github_id": user.get("github_name"), "dora_persons": candidates},
    )
