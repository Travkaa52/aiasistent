from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


def main_menu(is_admin: bool = False) -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="📨 Поддержка"), KeyboardButton(text="ℹ️ О боте")],
    ]
    if is_admin:
        buttons.insert(0, [KeyboardButton(text="⚙️ Панель администратора")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def cancel_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True
    )


def remove_keyboard() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()
