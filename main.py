# -*- coding: utf-8 -*-
import os
import datetime
import requests
from dotenv import load_dotenv
from generator import (
    generate_post, generate_image_url,
    load_history, save_history, prune_history,
)
from vk_client import vk_post

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
VK_TOKEN = os.getenv("VK_TOKEN")
VK_GROUP_ID = os.getenv("VK_GROUP_ID")

def send_with_photo(text, image_bytes):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    try:
        data = {"chat_id": CHANNEL_ID, "caption": text, "parse_mode": "Markdown"}
        files = {"photo": ("post.jpg", image_bytes, "image/jpeg")}
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
    history = prune_history(load_history())
    print("Генерируем пост...")
    post_text, topic, ctype = generate_post(history)
    print("Скачиваем картинку...")
    image_bytes = None
    image_url = generate_image_url(topic, history)
    try:
        r = requests.get(image_url, timeout=90)
        r.raise_for_status()
        image_bytes = r.content
    except Exception as e:
        print(f"Image download failed: {e}")

    print("Отправляем в Telegram...")
    if image_bytes and send_with_photo(post_text, image_bytes):
        pass
    else:
        send_message(post_text)

    if VK_TOKEN and VK_GROUP_ID:
        print("Отправляем во VK...")
        try:
            vk_post(VK_TOKEN, VK_GROUP_ID, post_text, image_bytes)
        except Exception as e:
            print(f"VK failed: {e}")

    history.append({
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "topic": topic,
        "type": ctype,
        "image_url": image_url,
    })
    save_history(history)
    print("Post published!")