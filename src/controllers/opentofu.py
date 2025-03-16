import logging
from typing import Dict

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
)
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_session
from src.services.state import StateService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["opentofu"])


async def get_state_service(session: AsyncSession = Depends(get_session)) -> StateService:
    return StateService(session)


@router.get("/state_identifier", status_code=status.HTTP_200_OK)
async def get_state(state_service: StateService = Depends(get_state_service)):
    """
    Get the OpenTofu state.
    """
    state_data = await state_service.get_state("state_identifier")
    if not state_data:
        raise HTTPException(status_code=404, detail="State not found")
    return state_data


@router.post("/state_identifier", status_code=status.HTTP_200_OK)
async def save_state(request: Request, state_service: StateService = Depends(get_state_service)):
    """
    Save the OpenTofu state.
    """
    state_data = await request.body()
    await state_service.save_state("state_identifier", state_data)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "ok"})


@router.api_route("/state_identifier/lock", methods=["LOCK"], status_code=status.HTTP_200_OK)
async def lock_state(request: Request, state_service: StateService = Depends(get_state_service)):
    """
    Lock the OpenTofu state.
    """
    lock_data = await request.json()
    lock_id = lock_data.get("ID")
    info = lock_data.get("Info", "")

    if not lock_id:
        raise HTTPException(status_code=400, detail="Lock ID is required")

    success = await state_service.lock_state("state_identifier", lock_id, info)
    if not success:
        raise HTTPException(status_code=409, detail="State is already locked")

    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "ok"})


@router.api_route("/state_identifier/unlock", methods=["UNLOCK"], status_code=status.HTTP_200_OK)
async def unlock_state(request: Request, state_service: StateService = Depends(get_state_service)):
    """
    Unlock the OpenTofu state.
    """
    lock_data = await request.json()
    lock_id = lock_data.get("ID")

    if not lock_id:
        raise HTTPException(status_code=400, detail="Lock ID is required")

    success = await state_service.unlock_state("state_identifier", lock_id)
    if not success:
        raise HTTPException(status_code=409, detail="Invalid lock ID")

    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "ok"})
