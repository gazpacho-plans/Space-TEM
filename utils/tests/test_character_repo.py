import os
from pathlib import Path

import pytest

from storage.character_repo import CharacterRepository


@pytest.mark.asyncio
async def test_character_repo_create_read_delete():
    # Use a dedicated test DB under data/db/
    db_path = Path("data/db/test.db")
    if db_path.exists():
        db_path.unlink()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    repo = CharacterRepository(db_path=str(db_path))

    # Create two characters for the same user
    ch1 = {
        "user_id": 1111,
        "name": "Alpha",
        "faction": "Faction A",
        "profession": "Spy",
        "attributes": {"Science": 3},
        "traits": ["Curious"],
        "income": {"money": 10, "influence": 0, "operations": 0, "research": 0, "boost": 0},
        "xp": 0,
        "location": "Earth",
        "controlled_orgs": [],
    }
    ch2 = {
        "user_id": 1111,
        "name": "Beta",
        "faction": "Faction B",
        "profession": "Hacker",
        "attributes": {"Science": 5},
        "traits": [],
        "income": {"money": 0, "influence": 2, "operations": 0, "research": 1, "boost": 0},
        "xp": 0,
        "location": "Mars",
        "controlled_orgs": [],
    }

    ch1_id = await repo.save_character(ch1)
    ch2_id = await repo.save_character(ch2)
    assert isinstance(ch1_id, int) and isinstance(ch2_id, int)
    assert ch2_id > ch1_id

    # Read latest by user
    latest = await repo.get_character_by_user(1111)
    assert latest is not None
    assert latest["id"] == ch2_id
    assert latest["name"] == "Beta"

    # List by user
    chars = await repo.list_characters_by_user(1111)
    assert len(chars) == 2
    assert {c["id"] for c in chars} == {ch1_id, ch2_id}

    # Delete the latest using the user+id path
    ok = await repo.delete_character(1111, ch2_id)
    assert ok is True
    remaining = await repo.get_character_by_user(1111)
    assert remaining is not None
    assert remaining["id"] == ch1_id

    # Delete the remaining using the by-id path
    ok2 = await repo.delete_character_by_id(ch1_id)
    assert ok2 is True

    # Confirm nothing remains for the user
    none = await repo.get_character_by_user(1111)
    assert none is None
    empty = await repo.list_characters_by_user(1111)
    assert empty == []

    await repo.aclose()

    # Cleanup test DB file
    if db_path.exists():
        db_path.unlink()


@pytest.mark.asyncio
async def test_unique_name_per_user():
    db_path = Path("data/db/test_unique.db")
    if db_path.exists():
        db_path.unlink()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    repo = CharacterRepository(db_path=str(db_path))

    base = {
        "name": "DupName",
        "faction": "Faction A",
        "profession": "Spy",
        "attributes": {"Science": 1},
        "traits": [],
        "income": {"money": 0, "influence": 0, "operations": 0, "research": 0, "boost": 0},
        "xp": 0,
        "location": "Earth",
        "controlled_orgs": [],
    }

    c1 = dict(base, user_id=1)
    c2_same_user_dup = dict(base, user_id=1)
    c3_other_user_same_name = dict(base, user_id=2)

    id1 = await repo.save_character(c1)
    assert isinstance(id1, int)

    with pytest.raises(ValueError):
        await repo.save_character(c2_same_user_dup)

    # Different user with same name should be allowed
    id3 = await repo.save_character(c3_other_user_same_name)
    assert isinstance(id3, int)
    assert id3 != id1

    await repo.aclose()

    if db_path.exists():
        db_path.unlink()


