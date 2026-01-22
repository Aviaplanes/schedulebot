# database/db.py
import json
import os
from typing import Any, Dict, List

from config import DATABASE_PATH, DEFAULT_GROUP, SCHEDULE_CACHE_PATH

# ============ USERS ============


def _load_db() -> Dict[str, Any]:
    """Загружает данные из JSON файла."""
    if not os.path.exists(DATABASE_PATH):
        return {"users": {}}

    try:
        with open(DATABASE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"users": {}}


def _save_db(data: Dict[str, Any]) -> None:
    """Сохраняет данные в JSON файл."""
    with open(DATABASE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


async def init_db() -> None:
    """Инициализация базы данных."""
    if not os.path.exists(DATABASE_PATH):
        _save_db({"users": {}})

    if not os.path.exists(SCHEDULE_CACHE_PATH):
        _save_cache({})


async def get_user_group(user_id: int) -> str:
    """Получает группу пользователя."""
    db = _load_db()
    user_data = db["users"].get(str(user_id))

    if user_data:
        return user_data.get("group_name", DEFAULT_GROUP)
    return DEFAULT_GROUP


async def set_user_group(user_id: int, group_name: str) -> None:
    """Устанавливает группу для пользователя."""
    db = _load_db()

    user_id_str = str(user_id)
    if user_id_str not in db["users"]:
        db["users"][user_id_str] = {}

    db["users"][user_id_str]["group_name"] = group_name
    _save_db(db)


async def user_exists(user_id: int) -> bool:
    """Проверяет, есть ли пользователь в базе."""
    db = _load_db()
    return str(user_id) in db["users"]


async def get_auto_send(user_id: int) -> bool:
    """Получает статус авто-рассылки для пользователя."""
    db = _load_db()
    user_data = db["users"].get(str(user_id))

    if user_data:
        return user_data.get("auto_send", False)
    return False


async def set_auto_send(user_id: int, enabled: bool) -> None:
    """Устанавливает статус авто-рассылки."""
    db = _load_db()

    user_id_str = str(user_id)
    if user_id_str not in db["users"]:
        db["users"][user_id_str] = {"group_name": DEFAULT_GROUP}

    db["users"][user_id_str]["auto_send"] = enabled
    _save_db(db)


async def get_users_with_auto_send() -> List[Dict[str, Any]]:
    """Возвращает список пользователей с включённой авто-рассылкой."""
    db = _load_db()
    users = []

    for user_id, user_data in db["users"].items():
        if user_data.get("auto_send", False):
            users.append(
                {
                    "user_id": int(user_id),
                    "group_name": user_data.get("group_name", DEFAULT_GROUP),
                }
            )

    return users


# ============ SCHEDULE CACHE ============


def _load_cache() -> Dict[str, Any]:
    """Загружает кэш расписания."""
    if not os.path.exists(SCHEDULE_CACHE_PATH):
        return {}

    try:
        with open(SCHEDULE_CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def _save_cache(data: Dict[str, Any]) -> None:
    """Сохраняет кэш расписания."""
    with open(SCHEDULE_CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


async def get_cached_schedule(weekday: int, group_name: str) -> List[str] | None:
    """Получает закэшированное расписание."""
    cache = _load_cache()
    key = f"{weekday}:{group_name}"
    return cache.get(key)


async def set_cached_schedule(
    weekday: int, group_name: str, lessons: List[str]
) -> None:
    """Сохраняет расписание в кэш."""
    cache = _load_cache()
    key = f"{weekday}:{group_name}"
    cache[key] = lessons
    _save_cache(cache)


async def get_cached_date(weekday: int) -> str | None:
    """Получает закэшированную дату расписания."""
    cache = _load_cache()
    return cache.get(f"date:{weekday}")


async def set_cached_date(weekday: int, date: str) -> None:
    """Сохраняет дату расписания в кэш."""
    cache = _load_cache()
    cache[f"date:{weekday}"] = date
    _save_cache(cache)
