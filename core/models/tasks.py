from datetime import datetime

from sqlalchemy import Text, DATETIME, func, TIMESTAMP, String
from sqlalchemy.orm import Mapped, mapped_column

from core.models.base import Base

class Task(Base):
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text,
                                             default="",
                                             server_default="",)
    completed: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP,
                                            default=datetime.now,
                                            server_default=func.now(),
                                            nullable=False,)
    due_at: Mapped[datetime] = mapped_column(TIMESTAMP,
                                             nullable=False,)
    completed_at: Mapped[datetime] = mapped_column(TIMESTAMP,
                                                   nullable=True)