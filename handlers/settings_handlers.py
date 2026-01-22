# handlers/settings_handlers.py
from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from config import AVAILABLE_GROUPS
from database import get_auto_send, get_user_group, set_auto_send, set_user_group
from keyboards import get_groups_keyboard, get_menu_keyboard, get_settings_keyboard

router = Router()


@router.message(F.text == "⚙️ Настройки")
async def settings_menu(message: Message):
    """Меню настроек."""
    current_group = await get_user_group(message.from_user.id)
    auto_send = await get_auto_send(message.from_user.id)

    await message.answer(
        f"⚙️ <b>Настройки</b>\n\n"
        f"📚 Текущая группа: <b>{current_group}</b>\n"
        f"🔔 Авто-рассылка: <b>{'ВКЛ' if auto_send else 'ВЫКЛ'}</b>\n\n"
        f"<i>Авто-рассылка отправит тебе уведомление, когда появится новое расписание.</i>",
        parse_mode="HTML",
        reply_markup=get_settings_keyboard(auto_send),
    )


@router.callback_query(F.data == "back_to_settings")
async def back_to_settings(callback: CallbackQuery):
    """Возврат в настройки."""
    current_group = await get_user_group(callback.from_user.id)
    auto_send = await get_auto_send(callback.from_user.id)

    await callback.message.edit_text(
        f"⚙️ <b>Настройки</b>\n\n"
        f"📚 Текущая группа: <b>{current_group}</b>\n"
        f"🔔 Авто-рассылка: <b>{'ВКЛ' if auto_send else 'ВЫКЛ'}</b>\n\n"
        f"<i>Авто-рассылка отправит тебе уведомление, когда появится новое расписание.</i>",
        parse_mode="HTML",
        reply_markup=get_settings_keyboard(auto_send),
    )
    await callback.answer()


@router.callback_query(F.data == "choose_group")
async def choose_group(callback: CallbackQuery):
    """Показывает список групп для выбора."""
    current_group = await get_user_group(callback.from_user.id)

    await callback.message.edit_text(
        "📚 <b>Выбери свою группу:</b>",
        parse_mode="HTML",
        reply_markup=get_groups_keyboard(current_group),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("set_group:"))
async def set_group(callback: CallbackQuery):
    """Устанавливает выбранную группу."""
    group_name = callback.data.split(":")[1]

    if group_name not in AVAILABLE_GROUPS:
        await callback.answer("❌ Неизвестная группа", show_alert=True)
        return

    await set_user_group(callback.from_user.id, group_name)
    auto_send = await get_auto_send(callback.from_user.id)

    await callback.message.edit_text(
        f"✅ Группа изменена на <b>{group_name}</b>!\n\n"
        f"⚙️ <b>Настройки</b>\n\n"
        f"📚 Текущая группа: <b>{group_name}</b>\n"
        f"🔔 Авто-рассылка: <b>{'ВКЛ' if auto_send else 'ВЫКЛ'}</b>",
        parse_mode="HTML",
        reply_markup=get_settings_keyboard(auto_send),
    )
    await callback.answer(f"Выбрана группа {group_name}")


@router.callback_query(F.data == "toggle_auto_send")
async def toggle_auto_send(callback: CallbackQuery):
    """Переключает авто-рассылку."""
    current_auto_send = await get_auto_send(callback.from_user.id)
    new_auto_send = not current_auto_send

    await set_auto_send(callback.from_user.id, new_auto_send)

    current_group = await get_user_group(callback.from_user.id)
    status = "включена ✅" if new_auto_send else "выключена ❌"

    await callback.message.edit_text(
        f"🔔 Авто-рассылка <b>{status}</b>\n\n"
        f"⚙️ <b>Настройки</b>\n\n"
        f"📚 Текущая группа: <b>{current_group}</b>\n"
        f"🔔 Авто-рассылка: <b>{'ВКЛ' if new_auto_send else 'ВЫКЛ'}</b>\n\n"
        f"<i>Авто-рассылка отправит тебе уведомление, когда появится новое расписание.</i>",
        parse_mode="HTML",
        reply_markup=get_settings_keyboard(new_auto_send),
    )
    await callback.answer(
        f"Авто-рассылка {'включена' if new_auto_send else 'выключена'}"
    )
