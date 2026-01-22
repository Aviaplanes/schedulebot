# handlers/schedule_handlers.py
import asyncio
from datetime import datetime, timedelta

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from config import DAY_NAMES, SCHEDULE_URLS
from database import get_user_group
from keyboards import get_menu_keyboard
from schedule import (
    fetch_schedule,
    format_schedule,
    parse_schedule,
    parse_schedule_date,
)

router = Router()


async def get_schedule_for_day(weekday: int, group_name: str) -> str:
    """Получает и форматирует расписание для дня недели."""
    day_name = DAY_NAMES.get(weekday, "")

    # Выходные
    if weekday > 4:
        return f"😴 {day_name} — выходной"

    url = SCHEDULE_URLS.get(weekday)
    if not url:
        return f"❌ Нет данных для {day_name}"

    # Загружаем HTML
    html = await fetch_schedule(url)
    if not html:
        return f"❌ Не удалось загрузить расписание на {day_name}"

    # Парсим
    lessons = parse_schedule(html, group_name)
    schedule_date = parse_schedule_date(html)

    # Формируем заголовок
    if schedule_date:
        header = f"📅 Расписание на {schedule_date}:"
    else:
        header = f"📅 {day_name}:"

    # Если группа не найдена
    if not lessons:
        return f"{header}\n\n❌ Группа {group_name} не найдена"

    # Форматируем расписание
    formatted = format_schedule(lessons, weekday)

    return f"{header}\n\n{formatted}"


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start."""
    group_name = await get_user_group(message.from_user.id)

    await message.answer(
        f"📚 Твоя группа: <b>{group_name}</b>\n\n"
        "Используй кнопки меню для просмотра расписания.\n"
        "Изменить группу можно в ⚙️ Настройки.",
        parse_mode="HTML",
        reply_markup=get_menu_keyboard(),
    )


@router.message(Command("menu"))
async def cmd_menu(message: Message):
    """Обработчик команды /menu."""
    group_name = await get_user_group(message.from_user.id)

    await message.answer(
        f"📚 Группа: <b>{group_name}</b>\n\nВыберите действие из меню ниже 👇🏻",
        parse_mode="HTML",
        reply_markup=get_menu_keyboard(),
    )


@router.message(F.text == "📅 Сегодня")
async def schedule_today(message: Message):
    """Расписание на сегодня."""
    today = datetime.now().weekday()
    group_name = await get_user_group(message.from_user.id)

    if today > 4:
        await message.answer(
            "😴 Сегодня выходной!\n\nИспользуй «📅 Завтра» или «📅 На неделю»"
        )
        return

    result = await get_schedule_for_day(today, group_name)
    await message.answer(result)


@router.message(F.text == "📅 Завтра")
async def schedule_tomorrow(message: Message):
    """Расписание на завтра."""
    tomorrow = (datetime.now() + timedelta(days=1)).weekday()
    group_name = await get_user_group(message.from_user.id)

    if tomorrow > 4:
        await message.answer(
            "😴 Завтра выходной!\n\nПоказываю расписание на понедельник:"
        )
        result = await get_schedule_for_day(0, group_name)
    else:
        result = await get_schedule_for_day(tomorrow, group_name)

    await message.answer(result)


@router.message(F.text == "📅 На неделю")
async def schedule_week(message: Message):
    """Расписание на всю неделю."""
    group_name = await get_user_group(message.from_user.id)

    for weekday in range(5):
        result = await get_schedule_for_day(weekday, group_name)
        await message.answer(result)
        await asyncio.sleep(0.1)
