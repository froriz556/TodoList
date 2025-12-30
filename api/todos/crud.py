from sqlalchemy.ext.asyncio import AsyncSession

from api.todos.schemas import CreateTask
from core.models.tasks import Task

async def create_task(session: AsyncSession, task_in: CreateTask):
    task = Task(**task_in.model_dump())
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task

async def get_all_tasks(session: AsyncSession):
    pass