import logging
from typing import Optional

from src.core.settings import StorageType, get_settings
from src.repos.storage.base import BaseStorageRepository
from src.repos.storage.minio_repos import MinioStorageRepository

logger = logging.getLogger(__name__)


def create_storage_repository(storage_type: Optional[StorageType] = None) -> BaseStorageRepository:

    REPOSITORIES = {
        StorageType.MINIO: MinioStorageRepository,
        # StorageType.AWS_S3: AwsS3StorageRepository, # TODO: Add AWS S3 storage repository
    }

    settings = get_settings()
    storage_type = storage_type or settings.STORAGE_TYPE

    repository_class = REPOSITORIES.get(storage_type)

    if repository_class is None:
        logger.error(f"Unsupported storage type: {storage_type}")
        raise ValueError(f"Unsupported storage type: {storage_type}")

    return repository_class()
