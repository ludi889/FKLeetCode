# backend/tests/conftest.py
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from typing import AsyncGenerator

import app.db.base  # noqa: F401
from app.db.base_class import Base
from app.db.session import get_db
from app.core.config import settings
from app.main import app
from scripts.seed import seed_database

TEST_DATABASE_URL = (
    f"postgresql+asyncpg://{settings.postgres_user}:{settings.postgres_password}"
    f"@localhost:5432/test_db"
)

DEFAULT_DATABASE_URL = (
    f"postgresql+asyncpg://{settings.postgres_user}:{settings.postgres_password}"
    f"@localhost:5432/postgres"
)

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)

@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_test_db_if_not_exists():
    """Automatically creates the test database before any tests run."""
    default_engine = create_async_engine(DEFAULT_DATABASE_URL, isolation_level="AUTOCOMMIT")
    
    async with default_engine.connect() as conn:
        result = await conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = 'test_db'")
        )
        exists = result.scalar_one_or_none()
        
        if not exists:
            await conn.execute(text("CREATE DATABASE test_db"))
            
    await default_engine.dispose()

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db_schema(create_test_db_if_not_exists):
    """Builds the database schema EXACTLY ONCE for the whole test session."""
    async with test_engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto"))
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        
    yield
    
    async with test_engine.begin() as conn:
        # Clean up cleanly at the very end
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture(scope="function")
async def db_session():
    """
    Yields a database session wrapped in a transaction.
    When the app calls `commit()`, it only commits a savepoint.
    When the test ends, the outer transaction rolls back automatically!
    """
    async with test_engine.connect() as connection:
        async with connection.begin() as transaction:
            session = AsyncSession(
                bind=connection, 
                join_transaction_mode="create_savepoint",
                expire_on_commit=False
            )
            
            yield session
            
            await session.close()
            await transaction.rollback()

@pytest_asyncio.fixture(scope="function")
async def seeded_db_session():
    """
    Yields a database session wrapped in a transaction.
    When the app calls `commit()`, it only commits a savepoint.
    When the test ends, the outer transaction rolls back automatically!
    """
    async with test_engine.connect() as connection:
        async with connection.begin() as transaction:
            session = AsyncSession(
                bind=connection, 
                join_transaction_mode="create_savepoint",
                expire_on_commit=False
            )
            await seed_database(session)
            
            yield session
            
            await session.close()
            await transaction.rollback()

async def _build_test_client(session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Private helper to yield a configured FastAPI client for a given DB session."""
    def override_get_db():
        return session

    app.dependency_overrides[get_db] = override_get_db
    
    async with app.router.lifespan_context(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            yield c
            
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    """Client with an empty database."""
    async for c in _build_test_client(db_session):
        yield c


@pytest_asyncio.fixture(scope="function")
async def seeded_client(seeded_db_session):
    """Client with a pre-seeded database."""
    async for c in _build_test_client(seeded_db_session):
        yield c