import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from src.controllers import health, opentofu
from src.core.logging import setup_logging
from src.settings import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()
setup_logging(settings)

API_PREFIX = "/api"


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Startup opentofu-state-manager-api app")
    yield
    logger.info("Shutdown opentofu-state-manager-api app")


def init_fastapi_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Store settings in app state for access in endpoints
    app.state.settings = settings

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

    # Include routers
    app.include_router(health.router)
    app.include_router(opentofu.router)
    return app


app = init_fastapi_app()
