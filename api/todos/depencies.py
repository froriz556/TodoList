from typing import Annotated

from fastapi import Depends, HTTPException, Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.todos.crud import get_room_member
from api.todos.schemas import GetRoom
from core.models import User, db_helper, Room, Room_Member
from core.security import get_current_user


async def get_current_room(
    room_id: Annotated[int, Path],
    user=Depends(get_current_user),
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    room = await session.execute(select(Room).where(Room.id == room_id))
    room = room.scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    room_member = await get_room_member(session, user, room)
    if not room_member:
        raise HTTPException(status_code=403, detail="Not a room member")
    return room


async def get_user_as_member_of_room(
    room=Depends(get_current_room),
    user=Depends(get_current_user),
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    room_member = await get_room_member(session, user, room)
    return room_member.scalar_one_or_none()
