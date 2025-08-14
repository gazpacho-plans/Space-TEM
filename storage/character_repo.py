import sqlite3
import json
from typing import Optional, Dict, Any, List
from pathlib import Path
import asyncio
import aiosqlite


class CharacterRepository:
    def __init__(self, db_path: str = "data/db/characters.db"):
        self.db_path = db_path
        self._conn: Optional[aiosqlite.Connection] = None
        self._init_lock = asyncio.Lock()
        self._initialized = False

    async def _ensure_initialized(self) -> None:
        if self._initialized and self._conn is not None:
            return
        async with self._init_lock:
            if self._initialized and self._conn is not None:
                return
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            conn = await aiosqlite.connect(self.db_path)
            # Improve concurrency characteristics
            await conn.execute("PRAGMA journal_mode=WAL;")
            await conn.execute("PRAGMA busy_timeout=5000;")
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS characters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    faction TEXT NOT NULL,
                    profession TEXT NOT NULL,
                    attributes TEXT NOT NULL,
                    traits TEXT NOT NULL,
                    income TEXT NOT NULL,
                    xp INTEGER NOT NULL,
                    location TEXT NOT NULL,
                    controlled_orgs TEXT NOT NULL
                );
                """
            )
            await conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_characters_user_id ON characters(user_id);
                """
            )
            # Enforce per-user unique character names
            try:
                await conn.execute(
                    """
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_characters_user_name
                    ON characters(user_id, name);
                    """
                )
            except Exception:
                # If duplicates already exist, index creation will fail; continue startup.
                pass
            await conn.commit()
            self._conn = conn
            self._initialized = True

    def close(self) -> None:
        """Schedule async close without blocking the caller (e.g., cog_unload)."""
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.aclose())
        except RuntimeError:
            # No running loop; best-effort synchronous close via sqlite3 for safety
            # (unlikely in bot runtime). We'll ignore since aiosqlite needs a loop.
            pass

    async def aclose(self) -> None:
        if self._conn is not None:
            try:
                await self._conn.close()
            finally:
                self._conn = None
                self._initialized = False

    def _serialize(self, character: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "user_id": character.get("user_id"),
            "name": character["name"],
            "faction": character["faction"],
            "profession": character["profession"],
            "attributes": json.dumps(character.get("attributes", {})),
            "traits": json.dumps(character.get("traits", [])),
            "income": json.dumps(character.get("income", {})),
            "xp": character.get("xp", 0),
            "location": character.get("location", "Earth"),
            "controlled_orgs": json.dumps(character.get("controlled_orgs", [])),
        }

    def _deserialize(self, row: sqlite3.Row | tuple) -> Dict[str, Any]:
        return {
            "id": row[0],
            "user_id": row[1],
            "name": row[2],
            "faction": row[3],
            "profession": row[4],
            "attributes": json.loads(row[5]),
            "traits": json.loads(row[6]),
            "income": json.loads(row[7]),
            "xp": row[8],
            "location": row[9],
            "controlled_orgs": json.loads(row[10]),
        }

    async def save_character(self, character: Dict[str, Any]) -> int:
        await self._ensure_initialized()
        assert self._conn is not None
        data = self._serialize(character)
        try:
            cur = await self._conn.execute(
                """
                INSERT INTO characters (
                    user_id, name, faction, profession, attributes, traits, income, xp, location, controlled_orgs
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["user_id"], data["name"], data["faction"], data["profession"],
                    data["attributes"], data["traits"], data["income"], data["xp"],
                    data["location"], data["controlled_orgs"],
                ),
            )
            await self._conn.commit()
            return cur.lastrowid  # type: ignore[return-value]
        except aiosqlite.IntegrityError as exc:
            # Likely uniqueness on (user_id, name)
            raise ValueError("A character with this name already exists for this user.") from exc

    async def get_character_by_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        await self._ensure_initialized()
        assert self._conn is not None
        async with self._conn.execute(
            "SELECT * FROM characters WHERE user_id = ? ORDER BY id DESC LIMIT 1",
            (user_id,),
        ) as cur:
            row = await cur.fetchone()
            if row is None:
                return None
            return self._deserialize(row)

    async def list_characters_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        await self._ensure_initialized()
        assert self._conn is not None
        async with self._conn.execute(
            "SELECT * FROM characters WHERE user_id = ? ORDER BY id DESC",
            (user_id,),
        ) as cur:
            rows = await cur.fetchall()
            return [self._deserialize(row) for row in rows]

    async def delete_character(self, user_id: int, character_id: int) -> bool:
        await self._ensure_initialized()
        assert self._conn is not None
        cur = await self._conn.execute(
            "DELETE FROM characters WHERE user_id = ? AND id = ?",
            (user_id, character_id),
        )
        await self._conn.commit()
        return cur.rowcount > 0  # type: ignore[return-value]

    async def list_all_characters(self, limit: int | None = None) -> List[Dict[str, Any]]:
        await self._ensure_initialized()
        assert self._conn is not None
        if limit is not None and limit > 0:
            async with self._conn.execute(
                "SELECT * FROM characters ORDER BY id DESC LIMIT ?",
                (limit,),
            ) as cur:
                rows = await cur.fetchall()
                return [self._deserialize(row) for row in rows]
        else:
            async with self._conn.execute(
                "SELECT * FROM characters ORDER BY id DESC"
            ) as cur:
                rows = await cur.fetchall()
                return [self._deserialize(row) for row in rows]

    async def delete_character_by_id(self, character_id: int) -> bool:
        await self._ensure_initialized()
        assert self._conn is not None
        cur = await self._conn.execute(
            "DELETE FROM characters WHERE id = ?",
            (character_id,),
        )
        await self._conn.commit()
        return cur.rowcount > 0  # type: ignore[return-value]
        