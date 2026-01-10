import os

from redis.asyncio import Redis

from core.security import create_password_hash


class RedisHelper:
    def __init__(self, url: str):
        self._url = url
        self._redis: Redis | None = None

    async def connect(self):
        if self._redis is not None:
            return
        self._redis = Redis.from_url(url=self._url, decode_responses=True)

    async def close(self):
        if self._redis:
            await self._redis.close()
            self._redis = None

    @property
    def conn(self) -> Redis:
        if not self._redis:
            raise RuntimeError("Redis is not connected")
        return self._redis


redis_helper = RedisHelper(os.getenv("REDIS_URL"))


class VerificationCodesCache:
    KEY_PREFIX = "confirm_code"

    def __init__(self, redis: Redis):
        self._redis = redis

    def _key(self, email: str):
        return f"{self.KEY_PREFIX}:{email}"

    async def get(self, email: str):
        return await self._redis.get(self._key(email))

    async def set(self, email: str, value: str, ttl: int = 300):
        await self._redis.set(self._key(email), value, ttl)

    async def delete(self, email: str):
        await self._redis.delete(self._key(email))


class ResetCodesCache(VerificationCodesCache):
    KEY_PREFIX = "reset_code"

    async def set(self, email: str, value: str, ttl: int = 300):
        hashed_value = create_password_hash(value)
        await self._redis.set(self._key(email), hashed_value, ttl)


confirm_codes_cache = None  # type: VerificationCodesCache | None
reset_codes_cache = None  # type: ResetCodesCache | None


def get_confirm_codes_cache() -> "VerificationCodesCache":
    if confirm_codes_cache is None:
        raise RuntimeError("Cache is not initialized yet")
    return confirm_codes_cache


def get_reset_codes_cache() -> "ResetCodesCache":
    if reset_codes_cache is None:
        raise RuntimeError("Cache is not initialized yet")
    return reset_codes_cache
