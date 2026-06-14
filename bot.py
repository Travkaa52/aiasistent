import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, LOG_LEVEL
from database import init_db
from middlewares.auth import AuthMiddleware
from middlewares.antispam import AntiSpamMiddleware
from handlers import admin, users, support


def setup_logging():
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("bot.log", encoding="utf-8"),
        ]
    )


async def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting corporate Business Bot...")

    # Инициализация базы данных
    try:
        await init_db()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.critical(f"Database initialization failed: {e}")
        return

    # Инициализация объекта бота
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # --- РЕГИСТРАЦИЯ MIDDLEWARES ---
    
    # 1. Слой для ЛС самого бота (управление, админка, инлайн-кнопки настроек)
    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())
    dp.message.middleware(AntiSpamMiddleware())
    dp.callback_query.middleware(AntiSpamMiddleware())
    
    # 2. БИЗНЕС-СЛОЙ: Направляем перехватчики на личные чаты твоего бизнес-аккаунта
    dp.business_message.middleware(AuthMiddleware())
    dp.business_message.middleware(AntiSpamMiddleware())

    # --- РЕГИСТРАЦИЯ РОУТЕРОВ (ПОРЯДОК СОБЛЮДЕН) ---
    dp.include_router(admin.router)    # Панель управления (в ЛС бота)
    dp.include_router(support.router)  # Модуль поддержки (если используется)
    dp.include_router(users.router)    # Обработчик бизнес-апдейтов (автоответы в твоих чатах)

    # Очищаем вебхуки
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Bot is running in Business Mode. Press Ctrl+C to stop.")

    try:
        # КРИТИЧЕСКИЙ ФИКС: Явно указываем Telegram, какие типы событий мы ждем.
        # Без "business_message" и "edited_business_message" пулинг будет игнорировать твои личные чаты.
        await dp.start_polling(
            bot,
            allowed_updates=[
                "message", 
                "callback_query", 
                "business_message", 
                "edited_business_message"
            ]
        )
    except Exception as e:
        logger.error(f"Error occurred during polling: {e}")
    finally:
        logger.info("Closing bot session...")
        await bot.session.close()
        logger.info("Bot stopped clean.")


if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot forced to stop by user.")
