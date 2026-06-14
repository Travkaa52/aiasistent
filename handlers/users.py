import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import StateFilter

from database import find_autoreply

logger = logging.getLogger(__name__)
router = Router()

# ВАЖНО: Команды /start и /help бизнес-бот ловить в чужих чатах не должен,
# так как это сломает логику общения с реальными клиентами.
# Этот хэндлер теперь обрабатывает ТОЛЬКО входящие сообщения от клиентов в твоем Бизнес-аккаунте.

@router.business_message(StateFilter(None))
async def handle_business_message(message: Message):
    """
    Обработка сообщений, приходящих в личные чаты твоего Telegram Business.
    """
    # Проверяем, что у сообщения есть текст или капшн
    trigger_text = message.text or message.caption
    if not trigger_text:
        return

    # Ищем автоответ в базе по триггеру
    autoreply = await find_autoreply(trigger_text.strip())
    if not autoreply:
        return

    rtype = autoreply["reply_type"]
    reply_text = autoreply.get("reply_text", "")
    caption_text = autoreply.get("caption") or reply_text

    # КРИТИЧЕСКИЙ НЮАНС: Для бизнес-сообщений нужно обязательно передавать business_connection_id,
    # чтобы Telegram понимал, от имени какого бизнес-аккаунта бот отправляет ответ.
    reply_kwargs = {
        "business_connection_id": message.business_connection_id,
        "parse_mode": "HTML"
    }

    try:
        if rtype == "text":
            # Используем message.answer — в Aiogram 3 он автоматически подхватит нужный chat_id клиента
            await message.answer(reply_text, **reply_kwargs)
            
        elif rtype == "photo":
            await message.answer_photo(
                photo=autoreply["file_id"],
                caption=caption_text,
                **reply_kwargs
            )
            
        elif rtype == "video":
            await message.answer_video(
                video=autoreply["file_id"],
                caption=caption_text,
                **reply_kwargs
            )
            
        elif rtype == "document":
            await message.answer_document(
                document=autoreply["file_id"],
                caption=caption_text,
                **reply_kwargs
            )
            
        logger.info(f"Отправлен бизнес-автоответ типа {rtype} в чат {message.chat.id}")
        
    except Exception as e:
        logger.error(f"Ошибка отправки бизнес-автоответа: {e}")
