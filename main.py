from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from api.todos import router as todos_router
from api.auth import router as auth_router
from core.models import Base, db_helper
import core.models.redis_helper as redis_module
from core.models.redis_helper import (
    redis_helper,
    VerificationCodesCache,
    ResetCodesCache,
    InvitesCodesCaches,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_helper.connect()
    redis_module.confirm_codes_cache = VerificationCodesCache(redis_helper.conn)
    redis_module.reset_codes_cache = ResetCodesCache(redis_helper.conn)
    redis_module.invites_codes_cache = InvitesCodesCaches(redis_helper.conn)
    async with db_helper.engine.begin() as coon:
        await coon.run_sync(Base.metadata.create_all)
    yield
    await redis_helper.close()


app = FastAPI(lifespan=lifespan)
app.include_router(router=auth_router)
app.include_router(router=todos_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
