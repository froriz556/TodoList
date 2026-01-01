from datetime import datetime

from sqlalchemy import Text, DATETIME, func, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from core.models.base import Base

class Task(Base):
    title: Mapped[str]
    description: Mapped[str] = mapped_column(Text,
                                             default="",
                                             server_default="",)
    completed: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[str] = mapped_column(TIMESTAMP,
                                            default=datetime.now(),
                                            server_default=func.now())
    due_at: Mapped[str] = mapped_column(TIMESTAMP)
    completed_at: Mapped[str] = mapped_column(TIMESTAMP)