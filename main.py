import os
import requests
import feedparser
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

def get_latest_news():
    # Официальная RSS-лента Федресурса (банкротства)
    rss_url = "https://fedresurs.ru/Rss.aspx"
    try:
        feed = feedparser.parse(rss_url)
        if feed.entries:
            latest = feed.entries[0]
            return f"📢 *Новое сообщение о банкротстве*\n\n📌 *{latest.title}*\n\n🔗 [Подробнее]({latest.link})"
        else:
            return "📢 *Тестовое сообщение*\n\nБот успешно подключен и готов к работе! Скоро здесь появятся актуальные новости о банкротстве."
    except Exception as e:
        return f"📢 *Тестовое сообщение*\n\nБот успешно подключен! (Временная ошибка парсинга RSS: {e})"

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("✅ Сообщение успешно отправлено в канал!")
    else:
        print(f"❌ Ошибка отправки: {response.status_code} - {response.text}")

if __name__ == "__main__":
    print("🔄 Получаем последние новости...")
    news_text = get_latest_news()
    send_message(news_text)
