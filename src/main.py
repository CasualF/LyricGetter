from fastapi import FastAPI

from src.config import app_configs, settings
from src.api import api_router

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from redis import asyncio as aioredis

from sqladmin import Admin
from src.database import engine
from src.admin.views import model_list
from src.admin.auth import authentication_backend


app = FastAPI(**app_configs)
app.include_router(api_router)


admin = Admin(app, engine, authentication_backend=authentication_backend)
for model in model_list:
    admin.add_view(model)


@app.on_event("startup")
async def startup():
    redis = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
                              encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="cache")


