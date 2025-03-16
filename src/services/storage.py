from abc import ABC, abstractmethod
from typing import Optional

from minio import Minio
from minio.error import S3Error

from src.settings import get_settings

settings = get_settings()


class StorageBackend(ABC):
    @abstractmethod
    async def get(self, path: str) -> Optional[bytes]:
        pass

    @abstractmethod
    async def put(self, path: str, data: bytes) -> None:
        pass

    @abstractmethod
    async def delete(self, path: str) -> None:
        pass


class MinIOStorageBackend(StorageBackend):
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        self.bucket = settings.MINIO_BUCKET_NAME

    async def get(self, path: str) -> Optional[bytes]:
        try:
            response = self.client.get_object(self.bucket, path)
            return response.read()
        except S3Error as e:
            if e.code == "NoSuchKey":
                return None
            raise

    async def put(self, path: str, data: bytes) -> None:
        self.client.put_object(self.bucket, path, data, len(data))

    async def delete(self, path: str) -> None:
        try:
            self.client.remove_object(self.bucket, path)
        except S3Error as e:
            if e.code != "NoSuchKey":
                raise
