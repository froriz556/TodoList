from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models import Base

if TYPE_CHECKING:
    from core.models.tasks import Task


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
