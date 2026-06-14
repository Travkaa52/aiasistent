import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from config import OWNER_ID
from database import is_manager, find_autoreply
from keyboards.reply import main_menu
from keyboards.inline import support_user_menu

logger = logging.getLogger(__name__)
router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    user = message.from_user
    admin = user.id == OWNER_ID or await is_manager(user.id)

    await message.answer(
        f"👋 Привет, <b>{user.first_name}</b>!\n\n"
        f"Я корпоративный бот для управления чатами и поддержки клиентов.\n\n"
        f"Используй меню ниже для навигации.",
        reply_markup=main_menu(is_admin=admin),
        parse_mode="HTML"
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "ℹ️ <b>Помощь</b>\n\n"
        "/start — Главное меню\n"
        "/help — Эта справка\n\n"
        "Нажмите <b>📨 Поддержка</b> для связи с менеджером.",
        parse_mode="HTML"
    )


@router.message(F.text == "ℹ️ О боте")
async def about_bot(message: Message):
    await message.answer(
        "🤖 <b>О боте</b>\n\n"
        "Корпоративный Telegram-бот для:\n"
        "• Управления чатами компании\n"
        "• Поддержки клиентов\n"
        "• Рассылок и автоответов\n"
        "• Аналитики и статистики\n\n"
        "По вопросам пишите в поддержку 👇",
        reply_markup=support_user_menu(),
        parse_mode="HTML"
    )


@router.message(F.text == "📨 Поддержка")
async def support_button(message: Message):
    await message.answer(
        "📨 <b>Поддержка</b>\n\n"
        "Напишите ваш вопрос, и наш менеджер ответит вам как можно скорее.",
        reply_markup=support_user_menu(),
        parse_mode="HTML"
    )


@router.message(F.chat.type == "private")
async def handle_private_message(message: Message):
    if not message.text:
        return

    autoreply = await find_autoreply(message.text)
    if autoreply:
        rtype = autoreply["reply_type"]
        if rtype == "text":
            await message.answer(autoreply["reply_text"], parse_mode="HTML")
        elif rtype == "photo":
            await message.answer_photo(
                photo=autoreply["file_id"],
                caption=autoreply["caption"] or autoreply["reply_text"]
            )
        elif rtype == "video":
            await message.answer_video(
                video=autoreply["file_id"],
                caption=autoreply["caption"] or autoreply["reply_text"]
            )
        elif rtype == "document":
            await message.answer_document(
                document=autoreply["file_id"],
                caption=autoreply["caption"] or autoreply["reply_text"]
            )
