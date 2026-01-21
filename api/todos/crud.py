from datetime import datetime
from typing import Annotated

from fastapi import HTTPException, Path, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from sqlalchemy.engine import Result

from api.todos.schemas import CreateTask, UpdateTask, CreateRoom, GetRoom
from core.models import db_helper, Room, Room_Member
from core.models.room_member import Roles
from core.models.tasks import Task, OwnerType
from core.models.users import User
from core.security import get_current_user

good_fields = ["created_at", "completed_at", "due_at", "completed"]


async def create_task(
    session: AsyncSession,
    task_in: CreateTask,
    user: User,
    owner_type: str = OwnerType.USER,
):
    task = Task(**task_in.model_dump(), user_id=user.id)
    if owner_type == OwnerType.USER:
        task.owner_type = OwnerType.USER
    if owner_type == OwnerType.ROOM:
        task.owner_type = OwnerType.ROOM
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


async def get_all_tasks(
    session: AsyncSession,
    order_by: str,
    user: User,
    owner_type: OwnerType = OwnerType.USER,
    room_id: int | None = None,
) -> list[Task]:
    order_status = "ASC"
    field = order_by
    if order_by.startswith("-"):
        field = order_by[1:]
        order_status = "DESC"
    if field in good_fields:
        stmt = select(Task)
        # .where(Task.user_id == user.id, Task.owner_type == owner_type)
        # .order_by(text(f"{field} {order_status}"))
        # )
        if owner_type == OwnerType.USER:
            stmt = stmt.where(Task.user_id == user.id, Task.owner_type == owner_type)
        elif owner_type == OwnerType.ROOM:
            if not room_id:
                raise HTTPException(status_code=400, detail="room id is required")
            stmt = stmt.where(Task.room_id == room_id, Task.owner_type == owner_type)
        else:
            raise HTTPException(status_code=400, detail="Invalid owner type")
        stmt = stmt.order_by(text(f"{field} {order_status}"))
    else:
        raise HTTPException(status_code=400, detail="Invalid ordering category")

    result: Result = await session.execute(stmt)
    tasks = result.scalars().all()
    return list(tasks)


async def get_task(
    session: AsyncSession,
    task_id: int,
    user: User,
    owner_type: str = "user",
    room_id: int = None,
):
    stmt = select(Task)
    if owner_type == OwnerType.USER:
        stmt = stmt.where(
            Task.id == task_id, Task.user_id == user.id, Task.owner_type == owner_type
        )
    elif owner_type == OwnerType.ROOM and room_id:
        stmt = stmt.where(
            Task.id == task_id, Task.room_id == room_id, Task.owner_type == owner_type
        )
    else:
        raise HTTPException(status_code=400, detail="Uncorrect owner type")
    result = await session.execute(stmt)
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


async def get_room_member(session: AsyncSession, user: User, room: Room):
    return await session.execute(
        select(Room_Member).where(
            Room_Member.room_id == room.id, Room_Member.user_id == user.id
        )
    )


async def create_room_and_creator(session: AsyncSession, room: CreateRoom, user: User):
    new_room = Room(**room.model_dump(), created_by=user.id)
    session.add(new_room)
    await session.flush()
    new_room_creator = Room_Member(
        role=Roles.CREATOR, user_id=user.id, room_id=new_room.id
    )
    session.add(new_room_creator)
    await session.commit()
    await session.refresh(new_room)
    await session.refresh(new_room_creator)
    return new_room


async def get_all_tasks_from_room(
    session: AsyncSession, user: User, room_id: int, order_by: str
):
    tasks = await get_all_tasks(
        session=session,
        user=user,
        owner_type=OwnerType.ROOM,
        room_id=room_id,
        order_by=order_by,
    )
    return tasks


async def assign_task_from_room_by_id(
    session: AsyncSession, user: User, room_id: int, task_id: int
):
    task = await get_task(session=session, task_id=task_id, user=user, room_id=room_id)
    if task is not None:
        setattr(task, "assigned_id", user.id)
        await session.commit()
        await session.refresh(task)
        return {"detail": f"Task was assigned by user with id {user.id}"}
    raise HTTPException(status_code=404, detail=f"Task with {task_id} id not found.")


async def get_task_from_room_by_id(
    session: AsyncSession, user: User, room_id: int, task_id: int
):
    task = await get_task(session=session, task_id=task_id, user=user, room_id=room_id)
    if task is not None:
        return task
    raise HTTPException(status_code=404, detail="Task not found.")


async def create_task_in_room(
    session: AsyncSession,
    user: User,
    task_in: CreateTask,
    room: Room,
    room_member: Room_Member,
):
    if room_member.role == Roles.CREATOR or room_member.role == Roles.ADMIN:
        task = Task(
            **task_in.model_dump(),
            room_id=room.id,
            owner_type=OwnerType.ROOM,
            user_id=user.id,
        )
        session.add(task)
        await session.commit()
        await session.refresh(task)
        return task
    raise HTTPException(status_code=403, detail="Doesn't have permissions")


async def only_complete_task_in_room(
    session: AsyncSession, user: User, room: Room, task_id: int
):
    task = await get_task(
        session=session,
        task_id=task_id,
        user=user,
        owner_type=OwnerType.ROOM,
        room_id=room.id,
    )
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    setattr(task, "completed", True)
    setattr(task, "completed_at", datetime.now())
    await session.commit()
    await session.refresh(task)
    return task


async def patch_task_in_room(
    session: AsyncSession,
    user: User,
    room: Room,
    room_member: Room_Member,
    task_in: UpdateTask,
    task_id: int,
):
    if room_member.role == Roles.MEMBER:
        raise HTTPException(status_code=403, detail="Doesn't have permissions")
    task = await get_task(
        session, task_id, user, room_id=room.id, owner_type=OwnerType.ROOM
    )
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    await patch_task(session=session, task=task, update_task=task_in)
    return task


async def accept_task(
    session: AsyncSession,
    user: User,
    room: Room,
    task_id: int,
):
    task = await get_task(
        session, task_id, user, owner_type=OwnerType.ROOM, room_id=room.id
    )
    if task.assigned_id is not None:
        raise HTTPException(status_code=409, detail="Task is already accept")
    task.assignee = user
    await session.commit()
    await session.refresh(task)
    return task


async def delete_task_in_room(
    session: AsyncSession,
    room_member: Room_Member,
    user: User,
    task_id: int,
    room: Room,
):
    if room_member.role == Roles.MEMBER:
        raise HTTPException(status_code=403, detail="Doesn't have permissions")
    task = await get_task(
        session=session,
        task_id=task_id,
        user=User,
        owner_type=OwnerType.ROOM,
        room_id=room.id,
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await delete_task(session=session, task=task)
