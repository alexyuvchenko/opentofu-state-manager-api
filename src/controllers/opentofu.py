import logging

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Request,
    status,
)
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.controllers.schema import (
    LockRequestSchema,
    LockResponseSchema,
    StateVersionListResponseSchema,
    StateVersionResponseSchema,
)
from src.core.auth import get_api_token
from src.db.session import get_session
from src.services.state import StateService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["opentofu"], dependencies=[Depends(get_api_token)])


async def get_state_service(session: AsyncSession = Depends(get_session)) -> StateService:
    return StateService(session)


@router.get("/state_identifier", status_code=status.HTTP_200_OK)
async def get_state(request: Request, state_service: StateService = Depends(get_state_service)):
    state_data = await state_service.get_state("state_identifier")
    logger.info(f"State data: {state_data}")
    return Response(content=state_data, media_type="application/json")


@router.post(
    "/state_identifier", status_code=status.HTTP_200_OK, response_model=LockResponseSchema
)
async def save_state(
    request: Request,
    ID: str = Query(str),
    state_service: StateService = Depends(get_state_service),
):
    state_data = await request.body()
    logger.info(f"Saving state with operation ID: {ID}")
    try:
        await state_service.save_state("state_identifier", state_data, operation_id=ID)
        logger.info(f"Successfully saved state for operation ID: {ID}")
        return LockResponseSchema()
    except ValueError as exc:
        logger.error(f"Failed to save state for operation ID {ID}: {str(exc)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.api_route(
    "/state_identifier/lock",
    methods=["LOCK"],
    status_code=status.HTTP_200_OK,
    response_model=LockResponseSchema,
)
async def lock_state(request: Request, state_service: StateService = Depends(get_state_service)):
    lock_data = LockRequestSchema.model_validate(await request.json())
    logger.info(f"Lock data: {lock_data}")
    success = await state_service.lock_state("state_identifier", lock_data)
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

    success = await state_service.unlock_state("state_identifier", lock_request.Id)
    if success is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lock ID not found")
    if not success:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Invalid lock ID")

    return LockResponseSchema()


@router.get(
    "/state_identifier/versions",
    status_code=status.HTTP_200_OK,
    response_model=StateVersionListResponseSchema,
)
async def get_state_versions(state_service: StateService = Depends(get_state_service)):
    versions = await state_service.get_state_versions("state_identifier")

    return StateVersionListResponseSchema(data=[version.model_dump() for version in versions])


@router.get(
    "/state_identifier/versions/{version_id}",
    status_code=status.HTTP_200_OK,
    response_model=StateVersionResponseSchema,
)
async def get_state_version(
    version_id: int, state_service: StateService = Depends(get_state_service)
):
    logger.info(f"Retrieving state version: {version_id}")
    version = await state_service.get_state_version("state_identifier", version_id)
    if not version:
        logger.warning(f"State version not found: {version_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"State version with id={version_id} not found",
        )
    logger.debug(f"Successfully retrieved state version: {version_id}")
    return StateVersionResponseSchema(**version.model_dump())
