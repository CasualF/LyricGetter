from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import NullPool
from src.config import settings


DB_USER = settings.DB_USER
DB_PASS = settings.DB_PASS
DB_HOST = settings.DB_HOST
DB_PORT = settings.DB_PORT
DB_NAME = settings.DB_NAME

TEST_DB_USER = settings.TEST_DB_USER
TEST_DB_PASS = settings.TEST_DB_PASS
TEST_DB_HOST = settings.TEST_DB_HOST
TEST_DB_PORT = settings.TEST_DB_PORT
TEST_DB_NAME = settings.TEST_DB_NAME

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
DATABASE_PARAMS = {}

TEST_DATABASE_URL = f"postgresql+asyncpg://{TEST_DB_USER}:{TEST_DB_PASS}@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}"

if settings.MODE == 'TEST':
    DATABASE_URL = TEST_DATABASE_URL
    DATABASE_PARAMS = {'poolclass': NullPool}

engine = create_async_engine(DATABASE_URL, **DATABASE_PARAMS)

AppSession = async_sessionmaker(bind=engine,
                                autoflush=False,
                                class_=AsyncSession,
                                expire_on_commit=False)


class Base(DeclarativeBase):
    pass
