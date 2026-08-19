import os
import asyncio
from telegram import Bot
from dotenv import load_dotenv
from generator import generate_post

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

async def main():
    bot = Bot(token=BOT_TOKEN)
    
    print("Grok ищет свежие законы и генерирует пост...")
    post_text = generate_post()
    
    print("Отправляем в Telegram канал...")
    await bot.send_message(
        chat_id=CHANNEL_ID,
        text=post_text
    )
    print("Пост успешно опубликован!")

if __name__ == "__main__":
    asyncio.run(main())
