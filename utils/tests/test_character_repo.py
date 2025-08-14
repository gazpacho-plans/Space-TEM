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

    # Create two characters with different users
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
        "user_id": 2222,
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

    # Read by user
    u1 = await repo.get_character_by_user(1111)
    u2 = await repo.get_character_by_user(2222)
    assert u1 is not None and u1["id"] == ch1_id
    assert u2 is not None and u2["id"] == ch2_id

    # List by user
    chars1 = await repo.list_characters_by_user(1111)
    chars2 = await repo.list_characters_by_user(2222)
    assert len(chars1) == 1 and chars1[0]["id"] == ch1_id
    assert len(chars2) == 1 and chars2[0]["id"] == ch2_id

    # Delete user 2222's character using the user+id path
    ok = await repo.delete_character(2222, ch2_id)
    assert ok is True
    # After deleting user 2222's character, user 1111's character remains
    remaining1 = await repo.get_character_by_user(1111)
    assert remaining1 is not None and remaining1["id"] == ch1_id

    # Delete the remaining using the by-id path
    ok2 = await repo.delete_character_by_id(ch1_id)
    assert ok2 is True

    # Confirm nothing remains for both users
    none1 = await repo.get_character_by_user(1111)
    assert none1 is None
    none2 = await repo.get_character_by_user(2222)
    assert none2 is None
    empty1 = await repo.list_characters_by_user(1111)
    empty2 = await repo.list_characters_by_user(2222)
    assert empty1 == [] and empty2 == []

    await repo.aclose()

    # Cleanup test DB file
    if db_path.exists():
        db_path.unlink()


@pytest.mark.asyncio
async def test_unique_constraints_one_per_user_and_global_name():
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

    # Same user attempting a second character should fail
    with pytest.raises(ValueError):
        await repo.save_character(c2_same_user_dup)

    # Different user with the same name should also fail (global name uniqueness)
    with pytest.raises(ValueError):
        await repo.save_character(c3_other_user_same_name)

    await repo.aclose()

    if db_path.exists():
        db_path.unlink()


