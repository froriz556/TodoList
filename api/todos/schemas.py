from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BaseTask(BaseModel):
    title: str
    description: str
    completed: bool = False


class CreateTask(BaseTask):
    due_at: datetime


class GetTask(BaseTask):
    created_at: datetime
    completed_at: datetime | None
    due_at: datetime | None
    model_config = ConfigDict(from_attributes=True)


class UpdateTask(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None
    due_at: datetime | None = None


class DeleteTask(BaseTask):
    pass


class BaseRoom(BaseModel):
    name: str


class CreateRoom(BaseRoom):
    pass


class GetRoom(BaseRoom):
    created_by: datetime
    created_at: datetime | None
    model_config = ConfigDict(from_attributes=True)
