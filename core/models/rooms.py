from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import func, TIMESTAMP, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.models import Base

if TYPE_CHECKING:
    from core.models import Task
    from core.models.room_member import Room_Member
    from core.models.users import User


class Room(Base):
    name: Mapped[str]
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    user: Mapped["User"] = relationship(back_populates="rooms")
    members: Mapped[list["Room_Member"]] = relationship(back_populates="user")
    tasks: Mapped[list["Task"]] = relationship(back_populates="room")
