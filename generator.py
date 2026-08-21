# -*- coding: utf-8 -*-
import os
import random
import re
import requests
import xml.etree.ElementTree as ET
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GROK_API_KEY")
AFFILIATE_LINK = os.getenv("AFFILIATE_LINK")
DEBT_LINK = "https://xn--j1ab.xn--90a1bg.xn--p1ai/invite/client/76b604d7-85ee-478a-8089-124d37fa6746"
AGENT_LINK = "https://xn--j1ab.xn--90a1bg.xn--p1ai/invite/agent/76b604d7-85ee-478a-8089-124d37fa6746"

TOPICS = [
    "списание долгов через банкротство физлиц",
    "права должников при звонках коллекторов",
    "банкротство через МФЦ без суда",
    "что не могут забрать коллекторы у должника",
    "арест зарплаты судебными приставами",
    "кредитные каникулы и реструктуризация",
]

CONTENT_TYPES = ["советы", "история", "объяснение", "новость"]

WORKING_MODELS = [
    "openai/gpt-oss-120b",
    "groq/compound",
    "qwen/qwen3.6-27b",
]

TYPE_INSTRUCTIONS = {
    "советы": "Напиши 3-5 практических советов",
    "история": "Напиши короткую историю человека, который законно избавился от долгов",
    "объяснение": "Объясни простыми словами один юридический термин или механизм",
    "новость": "Напиши пост на основе предоставленной новости",
}

def fetch_news():
    queries = ["банкротство физлиц", "списание долгов", "коллекторы закон права"]
    query = random.choice(queries)
    url = f"https://news.google.com/rss/search?q={query}&hl=ru&gl=RU&ceid=RU:ru"
    try:
        resp = requests.get(url, timeout=10)
        root = ET.fromstring(resp.content)
        items = root.findall(".//item")
        if items:
            item = random.choice(items[:10])
            title = item.findtext("title") or ""
            link = item.findtext("link") or ""
            source = title.split(" - ")[-1] if " - " in title else "Google Новости"
            return {"title": title, "link": link, "source": source}
    except Exception as e:
        print(f"News error: {e}")
    return None

def clean_thinking(text):
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

def generate_post():
    content_type = random.choice(CONTENT_TYPES)
    topic = random.choice(TOPICS)
    news = fetch_news() if content_type == "новость" else None
    if content_type == "новость" and not news:
        content_type = "объяснение"

    client = OpenAI(api_key=API_KEY, base_url="https://api.groq.com/openai/v1")

    news_block = f"Новость для поста: {news['title']}\n" if news else ""

    prompt = (
        "Ты юрист по списанию долгов и автор Telegram-канала. "
        f"Задача: {TYPE_INSTRUCTIONS[content_type]} на тему: {topic}. "
        f"{news_block}"
        "Пост до 900 знаков. Правила:\n"
        "1. Простыми словами, эмодзи для структуры.\n"
        "2. НЕ используй символы # и *.\n"
        "3. В конце добавь РОВНО 3 строки:\n"
        f"💸 [Избавиться от долгов]({DEBT_LINK})\n"
        f"👉 [Пройти опрос]({AFFILIATE_LINK})\n"
        f"🤝 [Хочу стать агентом]({AGENT_LINK})\n"
    )
    if news:
        prompt += f"4. После трёх строк добавь ещё одну: 📰 Источник: [{news['source']}]({news['link']})\n"
    else:
        prompt += "4. После трёх строк НИЧЕГО не добавляй, источника быть не должно.\n"
    prompt += "5. НЕ показывай рассуждения, только финальный пост.\n"

    for model in WORKING_MODELS:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=1000,
            )
            text = clean_thinking(response.choices[0].message.content)
            print(f"Groq answer ({model}), type={content_type}: {text[:80]}...")
            return text, topic
        except Exception as e:
            print(f"Model {model} failed: {e}")

    fallback = (
        "💡 Важная информация о долгах\n\n"
        "Законодательство в сфере банкротства постоянно обновляется, защищая права должников.\n\n"
        f"💸 [Избавиться от долгов]({DEBT_LINK})\n"
        f"👉 [Пройти опрос]({AFFILIATE_LINK})\n"
        f"🤝 [Хочу стать агентом]({AGENT_LINK})"
    )
    return fallback, topic

def generate_image_url(topic):
    p = f"clean professional illustration about {topic}, finance and law, calm colors, no text"
    return "https://image.pollinations.ai/prompt/" + requests.utils.quote(p) + "?width=1024&height=640&nologo=true"