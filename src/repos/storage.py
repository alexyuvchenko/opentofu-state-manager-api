import logging
from abc import ABC, abstractmethod
from typing import Optional

import aiobotocore.session
from botocore.exceptions import ClientError
from fastapi import HTTPException, status

from src.core.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class BaseStorageRepository(ABC):

    @abstractmethod
    async def get(self, path: str) -> Optional[bytes]:
        pass

    @abstractmethod
    async def put(self, path: str, data: bytes) -> None:
        pass

    @abstractmethod
    async def delete(self, path: str) -> None:
        pass

    @abstractmethod
    async def ensure_bucket_exists(self) -> None:
        pass


class MinioStorageRepository(BaseStorageRepository):

    def __init__(self):
        self.endpoint_url = (
            f"{'https' if settings.MINIO_SECURE else 'http'}://{settings.MINIO_ENDPOINT}"
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self.session = aiobotocore.session.get_session()
        self.client_kwargs = {
            "endpoint_url": self.endpoint_url,
            "aws_access_key_id": settings.MINIO_ACCESS_KEY,
            "aws_secret_access_key": settings.MINIO_SECRET_KEY,
        }

    async def _get_client(self):
        return self.session.create_client("s3", **self.client_kwargs)

    async def get(self, path: str) -> Optional[bytes]:
        try:
            async with await self._get_client() as client:
                response = await client.get_object(Bucket=self.bucket_name, Key=path)
                async with response["Body"] as stream:
                    return await stream.read()
        except ClientError as exc:
            logger.error(f"Got S3 error: {exc}")
            return None

    async def put(self, path: str, data: bytes) -> None:
        if not data or not isinstance(data, bytes):
            raise ValueError(f"Invalid data for S3 storage: {type(data)}")

        try:
            async with await self._get_client() as client:
                await client.put_object(
                    Bucket=self.bucket_name, Key=path, Body=data, ContentType="application/json"
                )
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Storage error: {str(exc)}",
            )

    async def delete(self, path: str) -> None:
        try:
            async with await self._get_client() as client:
                await client.delete_object(Bucket=self.bucket_name, Key=path)
        except ClientError as exc:
            logger.error(f"Got S3 error: {exc}")

    async def ensure_bucket_exists(self) -> None:
        try:
            async with await self._get_client() as client:
                try:
                    await client.head_bucket(Bucket=self.bucket_name)
                except ClientError:
                    await client.create_bucket(Bucket=self.bucket_name)
        except Exception as exc:
            logger.error(f"Error managing bucket: {exc}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"S3 error: {str(exc)}"
            )
