from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Text, DATETIME, func, TIMESTAMP, String, ForeignKey
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import Base
from core.models.mixins import UserRelationship

if TYPE_CHECKING:
    from core.models.rooms import Room
    from core.models.users import User


class OwnerType(Enum):
    USER = "user"
    ROOM = "room"


class Task(Base):
    _user_back_populates = "tasks"
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(
        Text,
        default="",
        server_default="",
    )
    completed: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    due_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
    )
    completed_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    owner_type: Mapped["OwnerType"] = mapped_column(
        SQLEnum(OwnerType, name="owner_type", native_enum=True), default=OwnerType.USER
    )
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), nullable=True)
    room: Mapped["Room"] = relationship(back_populates="tasks")

    assigned_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    assignee: Mapped["User"] = relationship(
        "User",
        back_populates="assigned_tasks",
        foreign_keys=[assigned_id],
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
    user: Mapped["User"] = relationship(
        "User", back_populates="tasks", foreign_keys=[user_id]
    )
