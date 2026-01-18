from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.users import User
from core.security import get_current_user
from .crud import (
    get_task_by_id,
    create_room_and_creator,
    get_all_tasks_from_room,
    create_task_in_room,
)
from api.todos.schemas import CreateTask, UpdateTask, GetTask, CreateRoom
from core.models import Task
from core.models.db_helper import db_helper
from api.todos import crud
from .depencies import get_current_room, get_user_as_member_of_room

router = APIRouter()


@router.get("/")
async def get_all_tasks(
    session: AsyncSession = Depends(db_helper.session_dependency),
    order_by: str = "created_at",
    user: User = Depends(get_current_user),
):
    return await crud.get_all_tasks(session=session, order_by=order_by, user=user)


@router.post("/", status_code=201)
async def create_task(
    task: CreateTask,
    session: AsyncSession = Depends(db_helper.session_dependency),
    user: User = Depends(get_current_user),
):
    return await crud.create_task(session=session, task_in=task, user=user)


@router.get("/{task_id}")
async def get_task(
    task_id: int,
    session: AsyncSession = Depends(db_helper.session_dependency),
    user: User = Depends(get_current_user),
):
    return await crud.get_task_by_id(task_id=task_id, session=session, user=user)


@router.patch("/{task_id}", response_model=GetTask)
async def patch_task(
    update_task: UpdateTask,
    session: AsyncSession = Depends(db_helper.session_dependency),
    task: Task = Depends(get_task_by_id),
):
    return await crud.patch_task(session=session, update_task=update_task, task=task)


@router.post("/{task_id}/completed", status_code=204)
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


@router.post("/rooms")
async def create_room(
    room: CreateRoom,
    session: AsyncSession = Depends(db_helper.session_dependency),
    user: User = Depends(get_current_user),
):
    return await create_room_and_creator(session, room, user)


@router.get("/rooms/{room_id}")
async def get_all_tasks_from_room_with_id(
    room_id: int,
    session: AsyncSession = Depends(db_helper.session_dependency),
    user: User = Depends(get_current_user),
    room_member=Depends(get_user_as_member_of_room),
    order_by: str = "created_at",
):
    if not room_member:
        raise HTTPException(status_code=403, detail="Not a room member")
    return await get_all_tasks_from_room(session, user, room_id, order_by)


@router.post("/rooms/{room_id}", response_model=GetTask)
async def create_new_task_in_room(
    task_in: CreateTask,
    session: AsyncSession = Depends(db_helper.session_dependency),
    user=Depends(get_current_user),
    room=Depends(get_current_room),
    room_member=Depends(get_user_as_member_of_room),
):
    if not room_member:
        raise HTTPException(status_code=403, detail="Not a room member")
    task = await create_task_in_room(
        session=session, user=user, room=room, task_in=task_in, room_member=room_member
    )
    return GetTask.model_validate(task)
