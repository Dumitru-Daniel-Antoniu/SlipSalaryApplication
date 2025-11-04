import os

from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


user = os.getenv("DATABASE_USER")
password = os.getenv("DATABASE_PASSWORD")
name = os.getenv("DATABASE_NAME")
host = os.getenv("DATABASE_HOST")
port = os.getenv("DATABASE_PORT")

engine = create_async_engine(
    f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}",
    echo=True,
    poolclass=NullPool
)
async_session = async_sessionmaker(engine, expire_on_commit=False)
