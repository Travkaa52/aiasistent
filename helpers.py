import logging
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

logger = logging.getLogger(__name__)


def is_admin_or_owner(user_id: int, owner_id: int, manager_ids: list) -> bool:
    return user_id == owner_id or user_id in manager_ids


async def broadcast_message(
    bot: Bot,
    user_ids: list,
    text: str,
    photo: str = None,
    reply_markup: InlineKeyboardMarkup = None
) -> dict:
    success = 0
    failed = 0

    for uid in user_ids:
        try:
            if photo:
                await bot.send_photo(
                    chat_id=uid,
                    photo=photo,
                    caption=text,
                    reply_markup=reply_markup
                )
            else:
                await bot.send_message(
                    chat_id=uid,
                    text=text,
                    reply_markup=reply_markup
                )
            success += 1
        except Exception as e:
            logger.warning(f"Failed to send broadcast to {uid}: {e}")
            failed += 1

    return {"success": success, "failed": failed}


def parse_buttons_from_text(text: str):
    lines = text.strip().split("\n")
    buttons = []
    message_lines = []
    in_buttons = False

    for line in lines:
        if line.strip().startswith("[") and "](" in line and line.strip().endswith(")"):
            in_buttons = True
            label = line.strip()[1:line.index("](")]
            url = line.strip()[line.index("](")+2:-1]
            buttons.append(InlineKeyboardButton(text=label, url=url))
        else:
            message_lines.append(line)

    markup = None
    if buttons:
        builder = InlineKeyboardBuilder()
        for btn in buttons:
            builder.row(btn)
        markup = builder.as_markup()

    return "\n".join(message_lines).strip(), markup


def format_stats(users_count: int, messages_count: int, managers_count: int) -> str:
    return (
        f"📊 <b>Статистика бота</b>\n\n"
        f"👥 Пользователей: <b>{users_count}</b>\n"
        f"💬 Сообщений: <b>{messages_count}</b>\n"
        f"👤 Менеджеров: <b>{managers_count}</b>"
    )


def format_analytics(daily: list, top_users: list) -> str:
    lines = ["📈 <b>Аналитика</b>\n"]

    lines.append("📅 <b>Активность по дням:</b>")
    if daily:
        for row in daily:
            lines.append(f"  {row['day']}: {row['count']} сообщений")
    else:
        lines.append("  Нет данных")

    lines.append("\n🏆 <b>Топ активных пользователей:</b>")
    if top_users:
        for i, u in enumerate(top_users, 1):
            name = u["full_name"] or u["username"] or str(u["telegram_id"])
            lines.append(f"  {i}. {name} — {u['msg_count']} сообщ.")
    else:
        lines.append("  Нет данных")

    return "\n".join(lines)
