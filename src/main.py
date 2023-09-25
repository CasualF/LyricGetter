from fastapi import FastAPI, HTTPException, Depends
from src.config import app_configs
from src.api import api_router


app = FastAPI(**app_configs)

app.include_router(api_router)
