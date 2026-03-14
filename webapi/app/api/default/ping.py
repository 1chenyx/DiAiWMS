from fastapi import APIRouter

_tag = "系统监控"
router = APIRouter()


@router.get(
    path="/ping",
    summary="ping",
)
async def ping():
    return "pong"
