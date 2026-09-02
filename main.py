# -*- coding: utf-8 -*-
import os
import datetime
import html
import requests
from dotenv import load_dotenv
from generator import (
    generate_post, generate_image_url,
    load_history, save_history, prune_history, DEBT_LINK, AFFILIATE_LINK, AGENT_LINK, format_readable,
)
from vk_client import vk_post
from max_client import max_post

load_dotenv()

POST_TYPE = os.getenv("POST_TYPE", "short")  # "short" или "longread"
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
VK_TOKEN = os.getenv("VK_TOKEN")
VK_GROUP_ID = os.getenv("VK_GROUP_ID")
VK_USER_TOKEN = os.getenv("VK_USER_TOKEN")
MAX_SESSION_B64 = os.getenv("MAX_SESSION_B64", "")
MAX_CHAT_ID = os.getenv("MAX_CHAT_ID", "")

def cta_footer():
    return "\n\n" + "\n".join([
        f'💸 <a href="{DEBT_LINK}">Избавиться от долгов</a>',
        f'👉 <a href="{AFFILIATE_LINK}">Пройти опрос</a>',
        f'🤝 <a href="{AGENT_LINK}">Хочу стать агентом</a>',
    ])

def safe_html(text):
    return html.escape(text, quote=False).replace("&amp;", "&")

def send_with_photo(text, image_bytes):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    try:
        data = {"chat_id": CHANNEL_ID, "caption": text, "parse_mode": "HTML"}
        files = {"photo": ("post.jpg", image_bytes, "image/jpeg")}
        r = requests.post(url, data=data, files=files, timeout=60)
        print(f"Telegram photo response: {r.status_code}")
        if r.status_code != 200:
            print(f"TG error: {r.text[:300]}")
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
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    r = requests.post(url, json=payload, timeout=30)
    print(f"Telegram response: {r.status_code}")
    if r.status_code != 200:
        print(f"TG error: {r.text[:300]}")
    r.raise_for_status()

def send_long_article(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    print(f"Longread length: {len(text)} chars")
    if len(text) > 4096:
        text = text[:4096]
        idx = text.rfind("\n")
        if idx > 3000:
            text = text[:idx]
        print("Longread hard-truncated to 4096")
    r = requests.post(url, json={
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }, timeout=30)
    print(f"Longread sent: {r.status_code}")
    if r.status_code != 200:
        print(f"TG error: {r.text[:300]}")
    return r.status_code == 200

if __name__ == "__main__":
    now = datetime.datetime.now(datetime.timezone.utc)
    event = os.getenv("GITHUB_EVENT_NAME", "")
    manual = event == "workflow_dispatch"
    skip_short = (now.hour == 10 and not manual)

    history = prune_history(load_history())

    if POST_TYPE in ("short", "both"):
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

        # Безопасное экранирование + HTML CTA
        clean = format_readable(post_text)
        if len(clean.strip()) < 80:
            print("WARNING: body too short, retrying generation...")
            retry_text, _t, _c = generate_post(history)
            clean = format_readable(retry_text)
        if len(clean.strip()) < 80:
            print("WARNING: using fallback text")
            clean = "Иногда достаточно одной минуты, чтобы понять: выход есть. Ответь на несколько вопросов и увидишь свой вариант - без звонков и обязательств."
        vk_text = clean + "\n\n" + "\n".join([
            f"💸 Избавиться от долгов: {DEBT_LINK}",
            f"👉 Пройти опрос: {AFFILIATE_LINK}",
            f"🤝 Хочу стать агентом: {AGENT_LINK}",
        ])
        post_text = safe_html(clean); print(f"Body length: {len(post_text)}"); post_text = post_text + cta_footer()

        print("Отправляем в Telegram...")
        if len(post_text) > 1024:
            print("Long caption: photo + text separately")
            teaser = clean[:150].rsplit(" ", 1)[0] + "..."
            if image_bytes:
                send_with_photo(teaser, image_bytes)
            send_message(post_text)
        elif image_bytes and send_with_photo(post_text, image_bytes):
            pass
        else:
            send_message(post_text)

        if VK_TOKEN and VK_GROUP_ID:
            print("Отправляем во VK...")
            try:
                vk_post(VK_TOKEN, VK_GROUP_ID, vk_text, image_bytes, image_url, VK_USER_TOKEN)
            except Exception as e:
                print(f"VK failed: {e}")

        history.append({
            "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "topic": topic,
            "type": ctype,
            "image_url": image_url,
        })
        save_history(history)
        if MAX_SESSION_B64 and MAX_CHAT_ID:
            print("Отправляем в MAX...")
            max_post(MAX_CHAT_ID, vk_text, image_url)
        print("Post published!")

    if POST_TYPE in ("longread", "both"):
        print("Готовим лонгрид для Дзена...")
        try:
            from generator import generate_dzen_article
            result = generate_dzen_article()
            if result:
                article, topic = result
                vk_long = article + "\n\n📢 Больше полезных материалов в нашем канале: https://t.me/AntiDolg_Vigivanie\n💸 Избавиться от долгов: " + DEBT_LINK + "\n👉 Пройти опрос: " + AFFILIATE_LINK + "\n🤝 Хочу стать агентом: " + AGENT_LINK
                article = safe_html(format_readable(article)) + '\n\n📢 Больше полезных материалов в нашем канале: <a href="https://t.me/AntiDolg_Vigivanie">t.me/AntiDolg_Vigivanie</a>' + cta_footer()
                ok = send_long_article(article)
                if ok and VK_TOKEN and VK_GROUP_ID:
                    print("Отправляем лонгрид во VK...")
                    try:
                        vk_post(VK_TOKEN, VK_GROUP_ID, vk_long, None, None, VK_USER_TOKEN)
                    except Exception as e:
                        print(f"VK longread failed: {e}")
                history.append({
                    "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    "topic": topic,
                    "type": "лонгрид",
                })
                save_history(history)
                if MAX_SESSION_B64 and MAX_CHAT_ID:
                    max_post(MAX_CHAT_ID, vk_long)
                    print("Longread published!")
        except Exception as e:
            print(f"Longread failed: {e}")