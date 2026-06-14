import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
OWNER_ID: int = int(os.getenv("OWNER_ID", "0"))
SUPPORT_GROUP_ID: int = int(os.getenv("SUPPORT_GROUP_ID", "0"))
DATABASE_PATH: str = os.getenv("DATABASE_PATH", "bot.db")
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

# ФИКС: Если ключа нет в .env, возвращаем пустую строку вместо None
GEMINI_KEY: str = os.getenv("GEMINI_KEY", "")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in .env file")
if not OWNER_ID:
    raise ValueError("OWNER_ID is not set in .env file")
