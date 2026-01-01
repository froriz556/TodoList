from fastapi import APIRouter

from api.todos.views import router as router_v1

router = APIRouter()
router.include_router(router=router_v1, prefix="/tasks")