import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import StateFilter

from database import find_autoreply
from utils.ai import generate_ai_reply  # Импортируем наш ИИ-модуль

logger = logging.getLogger(__name__)
router = Router()

@router.business_message(StateFilter(None))
async def handle_business_message(message: Message):
    """
    Умный обработчик личных бизнес-сообщений: БД + ИИ
    """
    trigger_text = message.text or message.caption
    if not trigger_text:
        return

    reply_kwargs = {
        "business_connection_id": message.business_connection_id,
        "parse_mode": "HTML"
    }

    # ЭТАП 1: Ищем жесткий автоответ в базе данных
    autoreply = await find_autoreply(trigger_text.strip())
    
    if autoreply:
        rtype = autoreply["reply_type"]
        reply_text = autoreply.get("reply_text", "")
        caption_text = autoreply.get("caption") or reply_text

        try:
            if rtype == "text":
                await message.answer(reply_text, **reply_kwargs)
            elif rtype == "photo":
                await message.answer_photo(autoreply["file_id"], caption=caption_text, **reply_kwargs)
            elif rtype == "video":
                await message.answer_video(autoreply["file_id"], caption=caption_text, **reply_kwargs)
            elif rtype == "document":
                await message.answer_document(autoreply["file_id"], caption=caption_text, **reply_kwargs)
            
            logger.info(f"Отправлен статический автоответ из БД в чат {message.chat.id}")
            return  # Завершаем, если нашли совпадение в БД
            
        except Exception as e:
            logger.error(f"Ошибка отправки статического автоответа: {e}")
            return

    # ЭТАП 2: Если в БД ничего не найдено — включается ИИ
    logger.info(f"Статических ответов не найдено. Отправляем запрос в Gemini для чата {message.chat.id}")
    
    # Генерируем ответ нейросетью
    ai_text = await generate_ai_reply(trigger_text.strip())
    
    if ai_text:
        try:
            # Отвечаем клиенту в личку от твоего имени
            await message.answer(ai_text, **reply_kwargs)
            logger.info(f"ИИ-ответ успешно отправлен в чат {message.chat.id}")
        except Exception as e:
            logger.error(f"Не удалось отправить ИИ-ответ: {e}")
