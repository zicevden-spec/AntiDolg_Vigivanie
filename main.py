# -*- coding: utf-8 -*-
import os
import requests
from dotenv import load_dotenv
from generator import generate_post

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHANNEL_ID, "text": text}
    response = requests.post(url, json=payload, timeout=30)
    response.raise_for_status()

if __name__ == "__main__":
    print("Grok генерирует пост...")
    post_text = generate_post()
    print("Отправляем в Telegram канал...")
    send_message(post_text)
    print("Post published!")
