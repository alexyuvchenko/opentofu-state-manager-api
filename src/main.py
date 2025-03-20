import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from src.controllers import health, opentofu
from src.core.logging import setup_logging
from src.core.settings import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()
setup_logging(settings)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Startup {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.debug(f"App configuration: title='{app.title}', docs_url='{app.docs_url}', environment='{settings.ENVIRONMENT.value}'")
    yield
    logger.info(f"Shutdown {settings.APP_NAME} v{settings.APP_VERSION}")


def init_fastapi_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.APP_VERSION,
        lifespan=lifespan,
    )

    app.state.settings = settings

    logger.debug("Configuring CORS middleware")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.debug(f"Configuring TrustedHost middleware with hosts: {settings.ALLOWED_HOSTS}")
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

    logger.debug("Including routers: health, opentofu")
    app.include_router(health.router)
    app.include_router(opentofu.router)

    return app


app = init_fastapi_app()
