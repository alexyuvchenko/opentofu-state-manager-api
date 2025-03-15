import logging
import sys

from json_log_formatter import JSONFormatter

from src.settings import LogFormat, Settings

logger = logging.getLogger(__name__)


def setup_logging(settings: Settings) -> None:
    fmt = "%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(lineno)d %(message)s  %(funcName)s"
    match settings.LOG_FORMAT:
        case LogFormat.JSON:
            formatter: logging.Formatter = JSONFormatter(fmt)
        case _:
            formatter = logging.Formatter(fmt)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logging.basicConfig(handlers=[handler], level=logging.INFO)
    logger.setLevel(logging.getLevelName(settings.LOG_LEVEL))
    for logger_name in ("fastapi", "uvicorn", "uvicorn.error", "uvicorn.access"):
        logging.getLogger(logger_name).handlers = [handler]
