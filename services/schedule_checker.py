# services/schedule_checker.py
import asyncio
from datetime import datetime
from typing import Dict, List, Set

from aiogram import Bot

from config import CHECK_INTERVAL, DAY_NAMES, SCHEDULE_URLS
from database import (
    get_cached_date,
    get_cached_schedule,
    get_users_with_auto_send,
    set_cached_date,
    set_cached_schedule,
)
from schedule import (
    fetch_schedule,
    format_schedule,
    parse_schedule,
    parse_schedule_date,
)


async def check_schedule_updates(bot: Bot) -> None:
    """
    Фоновая задача для проверки обновлений расписания.
    Запускается каждые CHECK_INTERVAL секунд.
    """
    print("🔄 Запущен чекер расписания")

    while True:
        try:
            await _check_all_days(bot)
        except Exception as e:
            print(f"❌ Ошибка в чекере расписания: {e}")

        await asyncio.sleep(CHECK_INTERVAL)


async def _check_all_days(bot: Bot) -> None:
    """Проверяет расписание на все дни недели."""
    # Получаем пользователей с авто-рассылкой
    users = await get_users_with_auto_send()

    if not users:
        return

    # Группируем пользователей по группам
    groups_to_check: Dict[str, List[int]] = {}
    for user in users:
        group_name = user["group_name"]
        user_id = user["user_id"]

        if group_name not in groups_to_check:
            groups_to_check[group_name] = []
        groups_to_check[group_name].append(user_id)

    # Проверяем каждый день недели
    for weekday in range(5):
        url = SCHEDULE_URLS.get(weekday)
        if not url:
            continue

        html = await fetch_schedule(url)
        if not html:
            continue

        # Проверяем дату расписания
        new_date = parse_schedule_date(html)
        cached_date = await get_cached_date(weekday)

        date_changed = new_date and new_date != cached_date

        if date_changed:
            await set_cached_date(weekday, new_date)
            print(f"📅 Обнаружена новая дата для {DAY_NAMES[weekday]}: {new_date}")

        # Проверяем расписание для каждой группы
        for group_name, user_ids in groups_to_check.items():
            await _check_group_schedule(
                bot=bot,
                html=html,
                weekday=weekday,
                group_name=group_name,
                user_ids=user_ids,
                date_changed=date_changed,
                schedule_date=new_date,
            )


async def _check_group_schedule(
    bot: Bot,
    html: str,
    weekday: int,
    group_name: str,
    user_ids: List[int],
    date_changed: bool,
    schedule_date: str,
) -> None:
    """Проверяет расписание для конкретной группы и рассылает при изменениях."""
    new_lessons = parse_schedule(html, group_name)
    cached_lessons = await get_cached_schedule(weekday, group_name)

    # Проверяем, изменилось ли расписание
    schedule_changed = new_lessons != cached_lessons

    if not schedule_changed and not date_changed:
        return

    # Сохраняем новое расписание в кэш
    await set_cached_schedule(weekday, group_name, new_lessons)

    # Если расписание не изменилось, но изменилась только дата — не рассылаем
    if not schedule_changed:
        return

    # Формируем сообщение
    day_name = DAY_NAMES.get(weekday, "")

    if schedule_date:
        header = f"🆕 <b>Новое расписание на {schedule_date}!</b>"
    else:
        header = f"🆕 <b>Новое расписание на {day_name}!</b>"

    if not new_lessons:
        message = f"{header}\n\n❌ Группа {group_name} не найдена в расписании"
    else:
        formatted = format_schedule(new_lessons, weekday)
        message = f"{header}\n\n{formatted}"

    # Рассылаем пользователям
    for user_id in user_ids:
        try:
            await bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode="HTML",
            )
            print(f"📨 Отправлено уведомление пользователю {user_id} ({group_name})")
        except Exception as e:
            print(f"❌ Не удалось отправить сообщение {user_id}: {e}")

        # Небольшая задержка, чтобы не спамить API
        await asyncio.sleep(0.1)
