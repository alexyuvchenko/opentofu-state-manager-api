import logging

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
)
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers.schema import LockRequestSchema, LockResponseSchema
from src.db.session import get_session
from src.services.state import StateService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["opentofu"])


async def get_state_service(session: AsyncSession = Depends(get_session)) -> StateService:
    return StateService(session)


@router.get("/state_identifier", status_code=status.HTTP_200_OK)
async def get_state(request: Request, state_service: StateService = Depends(get_state_service)):
    state_data = await state_service.get_state("state_identifier")
    if not state_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="State not found")

    return Response(content=state_data, media_type="application/json")


@router.post(
    "/state_identifier/{ID}", status_code=status.HTTP_200_OK, response_model=LockResponseSchema
)
async def save_state(request: Request, state_service: StateService = Depends(get_state_service)):
    state_data = await request.body()
    try:
        await state_service.save_state("state_identifier", state_data)
        return LockResponseSchema()
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.api_route(
    "/state_identifier/lock",
    methods=["LOCK"],
    status_code=status.HTTP_200_OK,
    response_model=LockResponseSchema,
)
async def lock_state(request: Request, state_service: StateService = Depends(get_state_service)):
    lock_request = LockRequestSchema.model_validate(await request.json())

    success = await state_service.lock_state(
        "state_identifier", lock_request.ID, lock_request.Info
    )
    if not success:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="State is already locked")

    return LockResponseSchema()


@router.api_route(
    "/state_identifier/unlock",
    methods=["UNLOCK"],
    status_code=status.HTTP_200_OK,
    response_model=LockResponseSchema,
)
async def unlock_state(request: Request, state_service: StateService = Depends(get_state_service)):
    lock_request = LockRequestSchema.model_validate(await request.json())

    success = await state_service.unlock_state("state_identifier", lock_request.ID)
    if not success:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Invalid lock ID")

    return LockResponseSchema()
