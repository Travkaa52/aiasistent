import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from database import add_user, is_banned, log_message
from config import OWNER_ID

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user = None

        if isinstance(event, Message):
            user = event.from_user
        elif isinstance(event, CallbackQuery):
            user = event.from_user

        if user:
            await add_user(
                telegram_id=user.id,
                username=user.username or "",
                full_name=user.full_name or ""
            )

            if user.id != OWNER_ID:
                banned = await is_banned(user.id)
                if banned:
                    if isinstance(event, Message):
                        await event.answer("🚫 Вы заблокированы в этом боте.")
                    elif isinstance(event, CallbackQuery):
                        await event.answer("🚫 Вы заблокированы.", show_alert=True)
                    return

            if isinstance(event, Message) and event.text:
                await log_message(user.id, event.text[:500], "incoming")

        return await handler(event, data)
