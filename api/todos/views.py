from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.models.db_helper import db_helper
from api.todos import crud
router = APIRouter()

@router.get("/")
async def get_all_tasks(session: AsyncSession = Depends(db_helper.session)):
    return await crud.get_all_tasks(session=session)
