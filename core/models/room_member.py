from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SQLEnum, TIMESTAMP, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.models import Base
from core.models.mixins import UserRelationship

if TYPE_CHECKING:
    from core.models.rooms import Room


class Roles(Enum):
    CREATOR = "creator"
    ADMIN = "admin"
    MEMBER = "member"


class Room_Member(Base, UserRelationship):
    _user_back_populates = "room_members"
    role: Mapped["Roles"] = mapped_column(
        SQLEnum(Roles, name="roles_enum", native_enum=True),
        default=Roles.MEMBER,
        nullable=False,
    )
    joined_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), nullable=False
    )
    room_id: Mapped["int"] = mapped_column(ForeignKey("rooms.id"))
    room: Mapped["Room"] = relationship(back_populates="room_members")
