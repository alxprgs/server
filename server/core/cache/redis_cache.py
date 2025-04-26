from fastapi import Request
from typing import Any

def _redis(request: Request):
    rc = request.app.state.redis_client
    if not request.app.state.redis_ok or not rc:
        return None
    return rc

async def cache_get(request: Request, key: str) -> Any | None:
    rc = _redis(request)
    if not rc:
        return None
    return await rc.get(key)

async def cache_set(request: Request, key: str, value: str, expire: int = 300) -> None:
    rc = _redis(request)
    if not rc:
        return
    await rc.set(key, value, ex=expire)

async def cache_delete(request: Request, *keys: str) -> None:
    rc = _redis(request)
    if not rc:
        return
    await rc.delete(*keys)
