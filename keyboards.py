# keyboards.py
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from config import AVAILABLE_GROUPS


def get_menu_keyboard() -> ReplyKeyboardMarkup:
    """Главное меню."""
    keyboard = [
        [KeyboardButton(text="📅 Сегодня"), KeyboardButton(text="📅 Завтра")],
        [KeyboardButton(text="📅 На неделю")],
        [KeyboardButton(text="⚙️ Настройки")],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def get_groups_keyboard(current_group: str) -> InlineKeyboardMarkup:
    """Клавиатура выбора группы."""
    buttons: list[list[InlineKeyboardButton]] = []
    row: list[InlineKeyboardButton] = []

    for group in AVAILABLE_GROUPS:
        if group == current_group:
            text = f"✅ {group}"
        else:
            text = group

        row.append(InlineKeyboardButton(text=text, callback_data=f"set_group:{group}"))

        if len(row) == 2:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    # Кнопка назад
    buttons.append(
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_settings")]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_settings_keyboard(auto_send: bool) -> InlineKeyboardMarkup:
    """Клавиатура настроек."""
    auto_send_text = "🔔 Авто-рассылка: ВКЛ" if auto_send else "🔕 Авто-рассылка: ВЫКЛ"

    buttons = [
        [InlineKeyboardButton(text="📚 Выбрать группу", callback_data="choose_group")],
        [InlineKeyboardButton(text=auto_send_text, callback_data="toggle_auto_send")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
