from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models import Base

if TYPE_CHECKING:
    from core.models.tasks import Task
    from core.models.room_member import Room_Member
    from core.models.rooms import Room


class User(Base):
    email: Mapped[str] = mapped_column(unique=True, index=True)
    password_hash: Mapped[str]
    is_verified: Mapped[bool] = mapped_column(default=False, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    tasks: Mapped[list["Task"]] = relationship(back_populates="user")
    assigned_tasks: Mapped[list["Task"]] = relationship(
        "Task", back_populates="assignee"
    )
    room_members: Mapped[list["Room_Member"]] = relationship(back_populates="user")
    rooms: Mapped[list["Room"]] = relationship(back_populates="user")
