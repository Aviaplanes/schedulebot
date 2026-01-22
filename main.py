# bot.py
import asyncio
import os

from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from database import init_db
from handlers import schedule_router, settings_router
from services import check_schedule_updates


async def main():
    """Точка входа."""
    if not BOT_TOKEN:
        print("❌ Токен бота не найден! Проверь .env файл.")
        return

    # Создаём папку для данных
    os.makedirs("data", exist_ok=True)

    # Инициализируем базу данных
    await init_db()
    print("✅ База данных инициализирована")

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Подключаем роутеры
    dp.include_router(schedule_router)
    dp.include_router(settings_router)

    # Запускаем фоновую задачу проверки расписания
    asyncio.create_task(check_schedule_updates(bot))

    print("✅ Бот запущен")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
