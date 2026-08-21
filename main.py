# -*- coding: utf-8 -*-
import os
import requests
from dotenv import load_dotenv
from generator import generate_post, generate_image_url

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

def send_with_photo(text, image_url):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    try:
        img = requests.get(image_url, timeout=90)
        img.raise_for_status()
        data = {"chat_id": CHANNEL_ID, "caption": text, "parse_mode": "Markdown"}
        files = {"photo": ("post.jpg", img.content, "image/jpeg")}
        r = requests.post(url, data=data, files=files, timeout=60)
        print(f"Telegram photo response: {r.status_code}")
        r.raise_for_status()
        return True
    except Exception as e:
        print(f"Photo failed: {e}")
        return False

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }
    r = requests.post(url, json=payload, timeout=30)
    print(f"Telegram response: {r.status_code}")
    r.raise_for_status()

if __name__ == "__main__":
    print("Генерируем пост...")
    post_text, topic = generate_post()
    print("Генерируем картинку...")
    image_url = generate_image_url(topic)
    print("Отправляем в канал...")
    if not send_with_photo(post_text, image_url):
        send_message(post_text)
    print("Post published!")