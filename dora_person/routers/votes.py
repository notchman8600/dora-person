"""Vote routes: casting votes, standing as a candidate and resetting counts."""

from typing import Any

from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse

from dora_person.config import Settings, get_settings
from dora_person.dependencies import get_current_user, get_vote_service
from dora_person.schemas import SubmitRequest
from dora_person.services.votes import VoteService

router = APIRouter(tags=["dora"])


@router.post("/submit")
async def submit_dora_person(
    message: str = Form(...),
    user: dict[str, Any] = Depends(get_current_user),
    service: VoteService = Depends(get_vote_service),
):
    request_dto = SubmitRequest(
        user_name=user.get("github_name"),
        message=message,
        avatar_url=user.get("avatar_url"),
    )
    if service.submit_candidacy(request_dto) is not None:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    return RedirectResponse(url="/vote", status_code=303)


@router.post("/vote")
async def store_vote_count(
    target_user_id: str = Form(...),
    user: dict[str, Any] = Depends(get_current_user),
    service: VoteService = Depends(get_vote_service),
):
    if service.record_vote(voter_id=user.get("github_name"), target_id=target_user_id) is not None:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    return RedirectResponse(url="/vote", status_code=303)


@router.get("/reset")
async def reset_vote_count(
    user: dict[str, Any] = Depends(get_current_user),
    service: VoteService = Depends(get_vote_service),
    settings: Settings = Depends(get_settings),
):
    if user.get("github_name") != settings.admin_github_name:
        raise HTTPException(status_code=403, detail="君にその権限はない")
    service.reset()
    return RedirectResponse(url="/vote", status_code=303)
