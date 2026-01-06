from datetime import datetime
from typing import Annotated

from fastapi import HTTPException, Path, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from sqlalchemy.engine import Result

from api.todos.schemas import CreateTask, UpdateTask
from core.models import db_helper
from core.models.tasks import Task
from core.models.users import User
from core.security import get_current_user

good_fields = ["created_at", "completed_at", "due_at", "completed"]


async def create_task(session: AsyncSession, task_in: CreateTask, user: User):
    task = Task(**task_in.model_dump(), user_id=user.id)
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


async def get_all_tasks(session: AsyncSession, order_by: str, user: User) -> list[Task]:
    order_status = "ASC"
    field = order_by
    if order_by.startswith("-"):
        field = order_by[1:]
        order_status = "DESC"
    if field in good_fields:
        stmt = (
            select(Task)
            .where(Task.user_id == user.id)
            .order_by(text(f"{field} {order_status}"))
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid ordering category")

    result: Result = await session.execute(stmt)
    tasks = result.scalars().all()
    return list(tasks)


async def get_task(session: AsyncSession, task_id: int, user: User):
    result = await session.execute(
        select(Task).where(Task.id == task_id, Task.user_id == user.id)
    )
    return result.scalar_one_or_none()


async def get_task_by_id(
    task_id: Annotated[int, Path],
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    task = await get_task(session=session, task_id=task_id, user=user)
    if task is not None:
        return task
    raise HTTPException(status_code=404, detail=f"Task with id:{task_id} not found")


async def patch_task(
    session: AsyncSession, update_task: UpdateTask, task: Task
) -> Task:
    data = update_task.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(task, k, v)
    if "completed" in data:
        task.completed_at = datetime.now() if task.completed else None
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
