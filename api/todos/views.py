from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .crud import get_task_by_id
from api.todos.schemas import CreateTask, UpdateTask, GetTask
from core.models import Task
from core.models.db_helper import db_helper
from api.todos import crud

router = APIRouter()


@router.get("/")
async def get_all_tasks(
    session: AsyncSession = Depends(db_helper.session_dependency),
    order_by: str = "created_at",
):
    return await crud.get_all_tasks(session=session, order_by=order_by)


@router.post("/", status_code=201)
async def create_task(
    task: CreateTask, session: AsyncSession = Depends(db_helper.session_dependency)
):
    return await crud.create_task(session=session, task_in=task)


@router.get("/{task_id}")
async def get_task(
    task_id: int, session: AsyncSession = Depends(db_helper.session_dependency)
):
    return await crud.get_task_by_id(task_id=task_id, session=session)


@router.patch("/{task_id}", response_model=GetTask)
async def patch_task(
    update_task: UpdateTask,
    session: AsyncSession = Depends(db_helper.session_dependency),
    task: Task = Depends(get_task_by_id),
):
    return await crud.patch_task(session=session, update_task=update_task, task=task)


@router.post("/{task_id}/completed", status_code=201)
async def patch_completed_task(
    session: AsyncSession = Depends(db_helper.session_dependency),
    task: Task = Depends(get_task_by_id),
):
    return await crud.patch_completed_task(
        session=session, task=task, is_completed=True
    )


@router.delete("/{task_id}")
async def delete_task(
    session: AsyncSession = Depends(db_helper.session_dependency),
    task: Task = Depends(get_task_by_id),
) -> None:
    await crud.delete_task(session=session, task=task)
