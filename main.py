# -*- coding: utf-8 -*-
import os
import requests
import feedparser
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

def get_latest_news():
    rss_url = "https://fedresurs.ru/Rss.aspx"
    try:
        feed = feedparser.parse(rss_url)
        if feed.entries:
            latest = feed.entries[0]
            return "Novoe soobschenie o bankrotstve: " + latest.title + " " + latest.link
    except Exception as e:
        print(f"RSS error: {e}")
    return "Test message. Bot is ready."

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHANNEL_ID, "text": text}
    response = requests.post(url, json=payload, timeout=30)
    response.raise_for_status()

if __name__ == "__main__":
    news_text = get_latest_news()
    send_message(news_text)
    print("Post published!")
