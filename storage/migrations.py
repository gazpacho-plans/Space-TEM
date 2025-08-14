import asyncio
from pathlib import Path
from typing import List, Set

import aiosqlite


# Increment this when you add a new migration step
CURRENT_SCHEMA_VERSION = 2


async def _ensure_meta_table(conn: aiosqlite.Connection) -> int:
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER NOT NULL
        );
        """
    )
    # Ensure there is exactly one row; initialize to version 0 if empty
    async with conn.execute("SELECT COUNT(*) FROM schema_version") as cur:
        row = await cur.fetchone()
        count = int(row[0]) if row else 0
    if count == 0:
        await conn.execute("INSERT INTO schema_version(version) VALUES (0)")
        await conn.commit()
        return 0
    async with conn.execute("SELECT version FROM schema_version LIMIT 1") as cur:
        row = await cur.fetchone()
        return int(row[0]) if row and row[0] is not None else 0


async def _set_schema_version(conn: aiosqlite.Connection, version: int) -> None:
    await conn.execute("UPDATE schema_version SET version = ?", (version,))
    await conn.commit()


async def _get_existing_columns(conn: aiosqlite.Connection, table: str) -> Set[str]:
    cols: Set[str] = set()
    async with conn.execute(f"PRAGMA table_info({table})") as cur:
        rows = await cur.fetchall()
        for row in rows:
            # row: cid, name, type, notnull, dflt_value, pk
            cols.add(str(row[1]))
    return cols


async def _add_column_if_missing(conn: aiosqlite.Connection, table: str, column_def_sql: str, column_name: str) -> None:
    cols = await _get_existing_columns(conn, table)
    if column_name not in cols:
        await conn.execute(f"ALTER TABLE {table} ADD COLUMN {column_def_sql}")


async def _ensure_characters_table(conn: aiosqlite.Connection) -> None:
    # Create table if it doesn't exist with the latest schema
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS characters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            faction TEXT NOT NULL,
            profession TEXT NOT NULL,
            attributes TEXT NOT NULL DEFAULT '{}',
            traits TEXT NOT NULL DEFAULT '[]',
            income TEXT NOT NULL DEFAULT '{}',
            xp INTEGER NOT NULL DEFAULT 0,
            location TEXT NOT NULL DEFAULT 'Earth',
            controlled_orgs TEXT NOT NULL DEFAULT '[]'
        );
        """
    )
    await conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_characters_user_id ON characters(user_id);
        """
    )
    # Unique per-user name if data allows; this may fail if duplicates already exist
    try:
        await conn.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_characters_user_name
            ON characters(user_id, name);
            """
        )
    except Exception:
        # Best-effort; if duplicates exist, keep going
        pass

    # Ensure any missing columns are added with safe defaults
    await _add_column_if_missing(conn, "characters", "attributes TEXT NOT NULL DEFAULT '{}'", "attributes")
    await _add_column_if_missing(conn, "characters", "traits TEXT NOT NULL DEFAULT '[]'", "traits")
    await _add_column_if_missing(conn, "characters", "income TEXT NOT NULL DEFAULT '{}'", "income")
    await _add_column_if_missing(conn, "characters", "xp INTEGER NOT NULL DEFAULT 0", "xp")
    await _add_column_if_missing(conn, "characters", "location TEXT NOT NULL DEFAULT 'Earth'", "location")
    await _add_column_if_missing(conn, "characters", "controlled_orgs TEXT NOT NULL DEFAULT '[]'", "controlled_orgs")


async def _migrate_from_0_to_1(conn: aiosqlite.Connection) -> None:
    await _ensure_characters_table(conn)


async def run_migrations(db_path: str = "data/db/characters.db") -> None:
    """Run schema migrations up to CURRENT_SCHEMA_VERSION.

    - Creates a tiny schema_version table (single-row) if missing
    - Applies additive, idempotent migrations that add defaulted columns
    """
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(db_path) as conn:
        # Improve concurrency characteristics
        await conn.execute("PRAGMA journal_mode=WAL;")
        await conn.execute("PRAGMA busy_timeout=5000;")

        version = await _ensure_meta_table(conn)

        if version < 1:
            await _migrate_from_0_to_1(conn)
            await _set_schema_version(conn, 1)

        # v2: enforce one character per user and global unique names (best-effort)
        if version < 2:
            try:
                await conn.execute(
                    """
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_characters_user_unique
                    ON characters(user_id);
                    """
                )
            except Exception:
                # If duplicates exist, index creation may fail; proceed
                pass

            try:
                await conn.execute(
                    """
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_characters_name_unique
                    ON characters(name);
                    """
                )
            except Exception:
                # If duplicates exist, index creation may fail; proceed
                pass

            await _set_schema_version(conn, 2)

        await conn.commit()


# Convenience for manual invocation during development
def migrate_sync(db_path: str = "data/db/characters.db") -> None:
    asyncio.run(run_migrations(db_path))


