from abc import ABC, abstractmethod
from typing import Optional


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
