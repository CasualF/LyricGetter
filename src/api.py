from fastapi import APIRouter

from src.account.router import router as user_router
from src.LyricGetter.router import router as songs_router

api_router = APIRouter(prefix='/api')

api_router.include_router(user_router, prefix="/users", tags=["users"])
api_router.include_router(songs_router, prefix='/songs', tags=['songs'])
