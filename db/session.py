from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

engine = create_async_engine(
    "postgresql+asyncpg://admin:password@postgres_db:5432/myapp",
    echo=True
)
async_session = async_sessionmaker(engine, expire_on_commit=False)
