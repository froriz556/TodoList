from datetime import datetime
from typing import Annotated

from fastapi import HTTPException, Path, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from sqlalchemy.engine import Result

from api.todos.schemas import CreateTask, UpdateTask
from core.models import db_helper
from core.models.tasks import Task

good_fields = ["created_at", "completed_at", "due_at", "completed"]


async def create_task(session: AsyncSession, task_in: CreateTask):
    task = Task(**task_in.model_dump())
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


async def get_all_tasks(session: AsyncSession, order_by: str) -> list[Task]:
    order_status = "ASC"
    field = order_by
    if order_by.startswith("-"):
        field = order_by[1:]
        order_status = "DESC"
    if field in good_fields:
        stmt = select(Task).order_by(text(f"{field} {order_status}"))
    else:
        raise HTTPException(status_code=400, detail="Invalid ordering category")

    result: Result = await session.execute(stmt)
    tasks = result.scalars().all()
    return list(tasks)


async def get_task(session: AsyncSession, task_id: int):
    return await session.get(Task, task_id)


async def get_task_by_id(
    task_id: Annotated[int, Path],
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    task = await get_task(session=session, task_id=task_id)
    if task is not None:
        return task
    raise HTTPException(status_code=404, detail=f"Task with id:{task_id} not found")


async def patch_task(
    session: AsyncSession, update_task: UpdateTask, task: Task
) -> Task:
    if update_task.completed:
        setattr(task, "completed_at", datetime.now())
    for k, v in update_task.model_dump(exclude_unset=True).items():
        setattr(task, k, v)
    await session.commit()
    await session.refresh(task)
    return task


async def patch_completed_task(session: AsyncSession, is_completed: bool, task: Task):
    setattr(task, "completed", is_completed)
    if is_completed:
        setattr(task, "completed_at", datetime.now())
    await session.commit()
    await session.refresh(task)
    return task


async def delete_task(session: AsyncSession, task: Task) -> None:
    await session.delete(task)
    await session.commit()
