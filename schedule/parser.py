# schedule/parser.py
import re
from typing import List

from bs4 import BeautifulSoup


def parse_schedule(html: str, group: str) -> List[str]:
    """
    Парсит расписание для конкретной группы из HTML.

    Ищет ячейку таблицы с названием группы,
    берёт строку ниже и тот же столбец — это ячейка с парами.
    Возвращает список строк вида "1) Предмет 305".
    """
    soup = BeautifulSoup(html, "html.parser")

    rows = soup.find_all("tr")
    if not rows:
        return []

    for i, row in enumerate(rows):
        cells = row.find_all("td")
        for j, cell in enumerate(cells):
            # Проверяем, есть ли название группы в ячейке
            if group in cell.get_text():
                # Строка с парами — следующая после строки с группой
                if i + 1 < len(rows):
                    next_row = rows[i + 1]
                    next_cells = next_row.find_all("td")

                    if j < len(next_cells):
                        schedule_cell = next_cells[j]

                        lessons: List[str] = []
                        for p in schedule_cell.find_all("p"):
                            text = p.get_text(strip=True)
                            # Отбрасываем пустые и неразрывный пробел
                            if text and text != "\xa0":
                                lessons.append(text)

                        return lessons

    return []


def parse_schedule_date(html: str) -> str:
    """
    Парсит дату расписания со страницы.

    Ищет <p style="text-align: center"> с текстом вида:
    "Расписание занятий на 15 апреля 2024 г."
    Возвращает строку в формате ДД.ММ.ГГГГ, например "15.04.2024".
    """
    soup = BeautifulSoup(html, "html.parser")

    # Ищем все <p> с center-стилем
    p_tags = soup.find_all("p", style=lambda x: x and "text-align: center" in x)

    months = {
        "января": "01",
        "февраля": "02",
        "марта": "03",
        "апреля": "04",
        "мая": "05",
        "июня": "06",
        "июля": "07",
        "августа": "08",
        "сентября": "09",
        "октября": "10",
        "ноября": "11",
        "декабря": "12",
    }

    for p in p_tags:
        text = p.get_text(strip=True)
        if "Расписание занятий на" in text:
            # Ищем шаблон "15 апреля 2024"
            match = re.search(r"(\d{1,2})\s+(\w+)\s+(\d{4})", text)
            if match:
                day = match.group(1).zfill(2)
                month_name = match.group(2).lower()
                year = match.group(3)

                month = months.get(month_name, "00")
                return f"{day}.{month}.{year}"

    return ""
