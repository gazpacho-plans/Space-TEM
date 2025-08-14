import sqlite3
import json
from typing import Optional, Dict, Any, List
from pathlib import Path
import concurrent.futures
import asyncio


class CharacterRepository:
    def __init__(self, db_path: str = "data/characters.db"):
        self.db_path = db_path
        self._executor: Optional[concurrent.futures.ThreadPoolExecutor] = None
        self._ensure_db()

    def _ensure_db(self) -> None:
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
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
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_characters_user_id ON characters(user_id);
                """
            )

    def _get_executor(self) -> concurrent.futures.ThreadPoolExecutor:
        if self._executor is None:
            self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        return self._executor

    def close(self) -> None:
        if self._executor:
            self._executor.shutdown(wait=False, cancel_futures=True)
            self._executor = None

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

    def _deserialize(self, row: sqlite3.Row) -> Dict[str, Any]:
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
        data = self._serialize(character)

        def _save() -> int:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.execute(
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
                return cur.lastrowid

        executor = self._get_executor()
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(executor, _save)

    async def get_character_by_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        def _get() -> Optional[Dict[str, Any]]:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.execute(
                    "SELECT * FROM characters WHERE user_id = ? ORDER BY id DESC LIMIT 1",
                    (user_id,),
                )
                row = cur.fetchone()
                if row is None:
                    return None
                return self._deserialize(row)

        executor = self._get_executor()
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(executor, _get)

    async def list_characters_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        def _list() -> List[Dict[str, Any]]:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.execute(
                    "SELECT * FROM characters WHERE user_id = ? ORDER BY id DESC",
                    (user_id,),
                )
                rows = cur.fetchall()
                return [self._deserialize(row) for row in rows]

        executor = self._get_executor()
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(executor, _list)

    async def delete_character(self, user_id: int, character_id: int) -> bool:
        def _delete() -> bool:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.execute(
                    "DELETE FROM characters WHERE user_id = ? AND id = ?",
                    (user_id, character_id),
                )
                return cur.rowcount > 0

        executor = self._get_executor()
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(executor, _delete)

    async def list_all_characters(self, limit: int | None = None) -> List[Dict[str, Any]]:
        def _list() -> List[Dict[str, Any]]:
            with sqlite3.connect(self.db_path) as conn:
                sql = "SELECT * FROM characters ORDER BY id DESC"
                if limit is not None and limit > 0:
                    sql += " LIMIT ?"
                    cur = conn.execute(sql, (limit,))
                else:
                    cur = conn.execute(sql)
                rows = cur.fetchall()
                return [self._deserialize(row) for row in rows]

        executor = self._get_executor()
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(executor, _list)

    async def delete_character_by_id(self, character_id: int) -> bool:
        def _delete() -> bool:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.execute(
                    "DELETE FROM characters WHERE id = ?",
                    (character_id,),
                )
                return cur.rowcount > 0

        executor = self._get_executor()
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(executor, _delete)