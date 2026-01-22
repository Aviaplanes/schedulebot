# schedule/formatter.py
import re
from typing import List

from config import LESSON_TIMES_DEFAULT, LESSON_TIMES_THURSDAY


def parse_lesson(lesson_text: str) -> tuple[str, str]:
    """
    Разбирает строку пары на название предмета и кабинет.
    Пример входа:
    "1) Математика 305" -> ("Математика", "305")
    """
    lesson_text = lesson_text.strip()

    if not lesson_text:
        return "", ""

    # Ищем номер кабинета в конце строки
    match = re.search(
        r"\s+(\d{3}|ЦОС|полигон|\(полигон\))$",
        lesson_text,
        re.IGNORECASE,
    )

    if match:
        room = match.group(1).strip("()")
        subject = lesson_text[: match.start()].strip()
    else:
        subject = lesson_text
        room = "—"

    return subject, room


def format_schedule(lessons: List[str], weekday: int) -> str:
    """
    Форматирует список строк-пар в красивое сообщение для Telegram.
    lessons: список строк вида "1) Предмет 305"
    weekday: номер дня недели (0 = понедельник, ..., 3 = четверг, и т.д.)
    """
    if not lessons:
        return "📭 Пар нет"

    formatted: list[str] = []
    is_thursday = weekday == 3

    # Добавляем классный час для четверга
    if is_thursday and 0 in LESSON_TIMES_THURSDAY:
        time_info = LESSON_TIMES_THURSDAY[0]
        # time_info: tuple("08:00-08:30", "Классный час")
        time_range, title = time_info
        formatted.append(f"📖 {title}\n⏰ {time_range}\n🏫 —")

    for lesson in lessons:
        # Извлекаем номер пары (1), (2) и т.д.
        match = re.match(r"^(\d+)\)\s*(.*)$", lesson)
        if not match:
            continue

        num = int(match.group(1))
        content = match.group(2).strip()
        if not content:
            continue

        subject, room = parse_lesson(content)

        # Выбираем время пары
        if is_thursday:
            time = LESSON_TIMES_THURSDAY.get(num, "—")
        else:
            time = LESSON_TIMES_DEFAULT.get(num, "—")

        # На четверг для num >= 1 время — строка, для 0 — кортеж
        if isinstance(time, tuple):
            time = time[0]

        formatted.append(f"📖 {subject}\n⏰ {time}\n🏫 {room}")

    if not formatted:
        return "📭 Пар нет"

    return "\n\n".join(formatted)
