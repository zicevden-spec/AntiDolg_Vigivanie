import os
import asyncio
from telegram import Bot
from dotenv import load_dotenv
from generator import generate_post

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

async def main():
    if not BOT_TOKEN or not CHANNEL_ID:
        print("? Ошибка: Проверьте переменные окружения")
        return
    
    bot = Bot(token=BOT_TOKEN)
    
    print("?? Grok генерирует пост...")
    post_text = generate_post()
    
    print("?? Отправляем в Telegram канал...")
    try:
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=post_text,
            parse_mode='Markdown'
        )
        print("? Пост успешно опубликован!")
    except Exception as e:
        print(f"? Ошибка при отправке: {e}")

if __name__ == "__main__":
    asyncio.run(main())
