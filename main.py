from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from api.todos import router as todos_router
from api.auth import router as auth_router
from core.models import Base, db_helper


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with db_helper.engine.begin() as coon:
        await coon.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router=auth_router)
app.include_router(router=todos_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
