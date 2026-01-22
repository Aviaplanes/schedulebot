# config.py
import os

from dotenv import load_dotenv

load_dotenv()

# Токен бота из .env
BOT_TOKEN = os.getenv("token")

# Группа по умолчанию (для новых пользователей)
DEFAULT_GROUP = "ИСП-21-24"

# Путь к базе данных (теперь JSON)
DATABASE_PATH = "data/users.json"

# Путь к кэшу расписания (для детекта изменений)
SCHEDULE_CACHE_PATH = "data/schedule_cache.json"

# Интервал проверки расписания (в секундах)
CHECK_INTERVAL = 300  # 5 минут

# Список всех доступных групп
AVAILABLE_GROUPS: list[str] = [
    "ИСП-11-25",
    "ИСП-21-24",
    "ИСП-31-23",
    "ИСП-41-22",
    "ИСП-42-22",
    "МСХП-11-25",
    "МСХП-21-24",
    "КСК-21-24",
    "ТМ-11-25",
    "ТМ-21-24",
    "ТМ-31-23",
    "ПК-11-25",
    "ПК-21-24",
    "ПК-31-23",
    "ПК-41-22",
]

# Расписание звонков (Пн, Вт, Ср, Пт)
LESSON_TIMES_DEFAULT: dict[int, str] = {
    1: "08:00-09:00",
    2: "09:10-10:10",
    3: "10:30-11:30",
    4: "11:45-12:45",
}

# Расписание звонков (Чт) — с классным часом
LESSON_TIMES_THURSDAY: dict[int, str | tuple[str, str]] = {
    0: ("08:00-08:30", "Классный час"),
    1: "08:35-09:35",
    2: "09:45-10:45",
    3: "11:05-12:05",
    4: "12:20-13:20",
}

# Ссылки на расписание по дням недели
SCHEDULE_URLS: dict[int, str] = {
    0: "https://sptkaluga.ru/pon",
    1: "https://sptkaluga.ru/vtor",
    2: "https://sptkaluga.ru/sreda",
    3: "https://sptkaluga.ru/chetv",
    4: "https://sptkaluga.ru/patn",
}

DAY_NAMES: dict[int, str] = {
    0: "Понедельник",
    1: "Вторник",
    2: "Среда",
    3: "Четверг",
    4: "Пятница",
}
