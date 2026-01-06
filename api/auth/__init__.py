from fastapi import APIRouter

from api.auth.views import router as router_v2

router = APIRouter()
router.include_router(router=router_v2)
