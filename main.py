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
VK_USER_TOKEN = os.getenv("VK_USER_TOKEN")

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

def send_long_article(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    chunks = []
    full = text
    while full:
        if len(full) <= 4096:
            chunks.append(full)
            break
        split_at = full.rfind("\n", 0, 4096)
        if split_at < 0:
            split_at = 4096
        chunks.append(full[:split_at])
        full = full[split_at:].lstrip()
    ok = True
    for i, ch in enumerate(chunks):
        r = requests.post(url, json={
            "chat_id": CHANNEL_ID,
            "text": ch,
            "disable_web_page_preview": True,
        }, timeout=30)
        print(f"Long article part {i+1}/{len(chunks)}: {r.status_code}")
        if r.status_code != 200:
            ok = False
    return ok

if __name__ == "__main__":
    now = datetime.datetime.now(datetime.timezone.utc)
    event = os.getenv("GITHUB_EVENT_NAME", "")
    manual = event == "workflow_dispatch"
    skip_short = (now.hour == 10 and not manual)

    history = prune_history(load_history())

    if not skip_short:
        print("Генерируем пост...")
        post_text, topic, ctype = generate_post(history)
        print("Скачиваем картинку...")
        image_url = generate_image_url(topic, history)
        image_bytes = None
        try:
            r = requests.get(image_url, timeout=90)
            r.raise_for_status()
            image_bytes = r.content
            print(f"Image from Pexels: {image_url}")
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
                vk_post(VK_TOKEN, VK_GROUP_ID, post_text, image_bytes, image_url, VK_USER_TOKEN)
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

    if now.hour == 10 or manual:
        print("Готовим лонгрид для Дзена...")
        try:
            from generator import generate_dzen_article
            result = generate_dzen_article()
            if result:
                article, topic = result
                ok = send_long_article(article)
                if ok and VK_TOKEN and VK_GROUP_ID:
                    print("Отправляем лонгрид во VK...")
                    try:
                        vk_post(VK_TOKEN, VK_GROUP_ID, article, None, None, VK_USER_TOKEN)
                    except Exception as e:
                        print(f"VK longread failed: {e}")
                history.append({
                    "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    "topic": topic,
                    "type": "лонгрид",
                })
                save_history(history)
                print("Longread published!")
        except Exception as e:
            print(f"Longread failed: {e}")