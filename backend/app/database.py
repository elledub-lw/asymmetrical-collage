from __future__ import annotations

import aiosqlite
from pathlib import Path
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any, Optional
import json

from .config import get_settings

DATABASE_PATH: Optional[str] = None


def get_db_path() -> str:
    global DATABASE_PATH
    if DATABASE_PATH is None:
        DATABASE_PATH = get_settings().database_url
    return DATABASE_PATH


async def init_db():
    """Initialize database with schema by running all migrations."""
    db_path = get_db_path()
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    migrations_dir = Path(__file__).parent.parent / "migrations"

    # Get all migration files sorted by name
    migration_files = sorted(migrations_dir.glob("*.sql"))

    async with aiosqlite.connect(db_path) as db:
        for migration_file in migration_files:
            with open(migration_file) as f:
                await db.executescript(f.read())
        await db.commit()


@asynccontextmanager
async def get_db() -> AsyncGenerator[aiosqlite.Connection, None]:
    """Get database connection."""
    db = await aiosqlite.connect(get_db_path())
    db.row_factory = aiosqlite.Row
    try:
        yield db
    finally:
        await db.close()


async def fetch_one(query: str, params: tuple = ()) -> Optional[dict]:
    """Fetch a single row as dict."""
    async with get_db() as db:
        cursor = await db.execute(query, params)
        row = await cursor.fetchone()
        if row:
            return dict(row)
        return None


async def fetch_all(query: str, params: tuple = ()) -> list[dict]:
    """Fetch all rows as list of dicts."""
    async with get_db() as db:
        cursor = await db.execute(query, params)
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def execute(query: str, params: tuple = ()) -> int:
    """Execute a query and return lastrowid."""
    async with get_db() as db:
        cursor = await db.execute(query, params)
        await db.commit()
        return cursor.lastrowid


async def execute_many(query: str, params_list: list[tuple]) -> None:
    """Execute a query with multiple parameter sets."""
    async with get_db() as db:
        await db.executemany(query, params_list)
        await db.commit()
