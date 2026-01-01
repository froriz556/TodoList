from typing import Annotated

from fastapi import HTTPException, Path, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.engine import Result

from api.todos.schemas import CreateTask, UpdateTask
from core.models import db_helper
from core.models.tasks import Task

async def create_task(session: AsyncSession, task_in: CreateTask):
    task = Task(**task_in.model_dump())
    session.add(task)
    await session.refresh(task)
    await session.commit()
    return task

async def get_all_tasks(session: AsyncSession) -> list[Task]:
    stmt = select(Task).order_by(Task.id)
    result: Result = await session.execute(stmt)
    tasks = result.scalars().all()
    return list(tasks)

async def get_task(session: AsyncSession, task_id: int):
    return await session.get(Task, task_id)

async def get_task_by_id( task_id: Annotated[int, Path], session: AsyncSession = Depends(db_helper.session_dependency)):
    task = await get_task(session=session, task_id=task_id)
    if task is not None:
        return task
    raise HTTPException(status_code=404, detail=f"Task with id:{task_id} not found")

async def patch_task(session: AsyncSession, update_task: UpdateTask, task: Task) -> Task:
    for k, v in update_task.model_dump(exclude_unset=True).items():
        setattr(task, k, v)
    await session.commit()
    await session.refresh(task)
    return task

async def patch_completed_task(session: AsyncSession, is_completed: bool, task: Task):
    setattr(task, "completed", is_completed)
    await session.commit()
    await session.refresh(task)
    return task

async def delete_task(session: AsyncSession, task: Task) -> None:
    await session.delete(task)

