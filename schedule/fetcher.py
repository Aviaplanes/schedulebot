# schedule/fetcher.py
import aiohttp


async def fetch_schedule(url: str) -> str | None:
    """Получает HTML страницы расписания по указанному URL."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    return await response.text()
                # Можно залогировать и другие статусы, если нужно
    except Exception as e:
        # Здесь можно подключить logging вместо print
        print(f"Ошибка загрузки расписания с {url}: {e}")
    return None
