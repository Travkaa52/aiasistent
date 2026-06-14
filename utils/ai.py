import logging
from google import genai
from google.genai import types
from config import GEMINI_KEY

logger = logging.getLogger(__name__)

# Инициализируем клиент Google GenAI
client = genai.Client(api_key=GEMINI_KEY)

# Системный промпт: жесткие правила поведения для ИИ
SYSTEM_INSTRUCTION = """
Ты — профессиональный ИИ-ассистент в личных чатах владельца бизнеса. 
Твоя цель — вежливо, кратко и по делу отвечать клиентам, помогать им с вопросами и подводить к сделке.

Правила:
1. Отвечай строго на том языке, на котором к тебе обратился клиент (русский / украинский / английский).
2. Пиши лаконично (1-3 предложения), не расписывай огромные тексты.
3. Будь вежлив, но держи деловой или дружелюбный тон (в зависимости от тона клиента).
4. Если клиент спрашивает то, чего ты не знаешь, или просит связаться с человеком, ответь, что владелец скоро освободится и ответит лично.
"""

async def generate_ai_reply(user_text: str) -> str:
    """
    Асинхронная обертка для генерации ответа от Gemini 2.5 Flash
    """
    try:
        # Так как библиотека синхронная, запускаем ее в отдельном потоке, чтобы не фризить бота
        response = await asyncio.to_thread(
            client.models.generate_content,
            model='gemini-2.5-flash',
            contents=user_text,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                max_output_tokens=300,  # Ограничиваем длину ответа
                temperature=0.7,        # Оптимальная креативность
            )
        )
        return response.text
    except Exception as e:
        logger.error(f"Ошибка генерации ответа через Gemini API: {e}")
        return ""
