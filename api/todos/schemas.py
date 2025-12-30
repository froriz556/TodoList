from pydantic import BaseModel


class BaseTask(BaseModel):
    title: str
    description: str
    completed: bool = False

class CreateTask(BaseTask):
    due_at: str

class GetTask(BaseTask):
    created_at: str
    completed_at: str
    due_at: str

class UpdateTask(BaseTask):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None
    due_at: str | None = None

class DeleteTask(BaseTask):
    pass