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
            # UTF-8 кодировка обязательна, чтобы логи не ломались на кириллице
            logging.FileHandler("bot.log", encoding="utf-8"),
        ]
    )


async def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting corporate bot...")

    # Инициализация базы данных (создание таблиц, подключение пула)
    try:
        await init_db()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.critical(f"Database initialization failed: {e}")
        return

    # Инициализация объекта бота с глобальным HTML-парсингом
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    # В продакшене MemoryStorage можно заменить на RedisStorage
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # --- РЕГИСТРАЦИЯ MIDDLEWARES ---
    # Глобальная авторизация, логирование и проверка банов (для сообщений и инлайн-кликов)
    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())
    
    # ФИКС: Регистрируем Антиспам-фильтр на оба канала входящих данных
    dp.message.middleware(AntiSpamMiddleware())
    dp.callback_query.middleware(AntiSpamMiddleware())

    # --- РЕГИСТРАЦИЯ РОУТЕРОВ (ПОРЯДОК СТРОГО СОБЛЮДЕН) ---
    dp.include_router(admin.router)    # 1. Админка (Проверяет права менеджеров первее всех)
    dp.include_router(support.router)  # 2. Саппорт (Перехватывает сообщения, если активен FSM-стейт диалога)
    dp.include_router(users.router)    # 3. Обычные юзеры (Ловит свободный текст и команды /start, /help)

    # Очищаем вебхуки и пропускаем сообщения, которые пришли, пока бот был выключен
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Bot is running. Press Ctrl+C to stop.")

    try:
        # Запуск бесконечного поллинга
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error occurred during polling: {e}")
    finally:
        # Корректное и безопасное закрытие всех сессий и соединений с Telegram API
        logger.info("Closing bot session...")
        await bot.session.close()
        logger.info("Bot stopped clean.")


if __name__ == "__main__":
    # Фикс для некоторых систем (особенно Windows / старые версии Linux на хостингах), 
    # чтобы принудительно использовать корректный Event Loop
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot forced to stop by user.")
