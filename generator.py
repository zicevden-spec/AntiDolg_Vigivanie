# -*- coding: utf-8 -*-
import os
import json
import random
import re
import datetime
import requests
import xml.etree.ElementTree as ET
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GROK_API_KEY")
AFFILIATE_LINK = os.getenv("AFFILIATE_LINK")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
DEBT_LINK = "https://xn--j1ab.xn--90a1bg.xn--p1ai/invite/client/76b604d7-85ee-478a-8089-124d37fa6746"
AGENT_LINK = "https://xn--j1ab.xn--90a1bg.xn--p1ai/invite/agent/76b604d7-85ee-478a-8089-124d37fa6746"

TOPICS = [
    "списание долгов через банкротство физлиц",
    "права должников при звонках коллекторов",
    "банкротство через МФЦ без суда",
    "что не могут забрать коллекторы у должника",
    "арест зарплаты судебными приставами",
    "кредитные каникулы и реструктуризация",
    "мифы о банкротстве: что правда, а что нет",
    "что происходит с квартирой и машиной при банкротстве",
    "единственное жильё при банкротстве: как закон его защищает",
    "банкротство и семья: влияет ли процедура на близких",
    "статистика банкротств физлиц в России",
    "как общаться с банками после банкротства",
    "жизнь после банкротства: чистый старт",
    "процедура банкротства пошагово",
    "сколько реально стоит банкротство",
    "банкротство пенсионеров: особенности",
    "банкротство самозанятых и ИП",
    "разница между банкротством через МФЦ и через суд",
    "когда банкротство НЕ нужно",
    "какие долги списываются, а какие нет",
    "можно ли выезжать за границу при банкротстве",
    "банкротство и алименты",
    "что происходит с ипотекой при банкротстве",
    "влияет ли банкротство на трудоустройство",
    "как выбрать юриста по банкротству и не попасть на мошенников",
    "мошенники в банкротстве: как распознать",
    "кто такой финансовый управляющий и какова его роль",
    "сколько по времени длится банкротство",
    "какие документы нужны для банкротства",
    "банкротство супругов и раздел имущества",
    "списываются ли долги по ЖКХ",
    "долги по распискам обычным людям и банкротство",
    "налоговые долги и банкротство",
    "штрафы ГИБДД и банкротство",
    "микрозаймы: как выбраться из долговой спирали",
    "поручительство по кредиту: чем рискует поручитель",
    "срок исковой давности по долгам",
    "кредитная история после банкротства",
    "где получить бесплатную юридическую помощь должнику",
    "передают ли долги по наследству",
]

CONTENT_TYPES = ["советы", "история", "объяснение", "новость", "статистика", "разбор мифа", "поддержка"]

WORKING_MODELS = [
    "openai/gpt-oss-120b",
    "groq/compound",
    "qwen/qwen3.6-27b",
]

TYPE_INSTRUCTIONS = {
    "советы": "Напиши 3-5 практических советов",
    "история": "Напиши короткую историю человека, который законно избавился от долгов и начал жизнь заново",
    "объяснение": "Объясни простыми словами один юридический термин или механизм",
    "новость": "Напиши пост на основе предоставленной новости",
    "статистика": "Напиши пост с цифрами и фактами о банкротстве физлиц в России",
    "разбор мифа": "Напиши в формате: МИФ (популярный страх) и РЕАЛЬНОСТЬ (как на самом деле по закону)",
    "поддержка": "Напиши спокойный поддерживающий пост, который снимает тревогу и даёт уверенность",
}

HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "history.json")

def load_history():
    try:
        with open(HISTORY_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False)

def prune_history(history):
    week_ago = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=7)
    out = []
    for e in history:
        try:
            if datetime.datetime.fromisoformat(e["ts"]) >= week_ago:
                out.append(e)
        except Exception:
            pass
    return out

def pick_combo(history):
    used = {(e.get("topic"), e.get("type")) for e in history}
    free = [(t, c) for t in TOPICS for c in CONTENT_TYPES if (t, c) not in used]
    if not free:
        free = [(t, c) for t in TOPICS for c in CONTENT_TYPES]
    return random.choice(free)

def image_query_for(topic):
    mapping = [
        ("коллектор", "phone stress"),
        ("МФЦ", "office documents service"),
        ("зарплат", "salary bank card"),
        ("квартир", "apartment home"),
        ("машиной", "car"),
        ("пенсионер", "pensioner family"),
        ("самозанят", "small business"),
        ("статистика", "chart statistics data"),
        ("миф", "law justice truth"),
        ("семья", "family support calm"),
        ("супруг", "couple marriage"),
        ("жизнь после", "freedom new start"),
        ("пошагово", "steps plan checklist"),
        ("документ", "papers documents"),
        ("стоит", "money calculator"),
        ("каникулы", "bank credit calendar"),
        ("микрозайм", "cash loan trap"),
        ("наследств", "inheritance family"),
        ("юрист", "lawyer office consultation"),
        ("мошенник", "fraud warning"),
        ("ипотек", "mortgage house"),
        ("алимент", "family children"),
        ("штраф", "traffic fine car"),
        ("ЖКХ", "utilities home"),
        ("кредитная история", "credit report"),
    ]
    for key, q in mapping:
        if key in topic:
            return q
    return "money finance law calm"

def fetch_news():
    queries = ["банкротство физлиц", "списание долгов", "коллекторы закон права", "банкротство статистика"]
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

def ensure_links(text):
    links = [
        ("💸 [Избавиться от долгов]({})".format(DEBT_LINK), DEBT_LINK),
        ("👉 [Пройти опрос]({})".format(AFFILIATE_LINK), AFFILIATE_LINK),
        ("🤝 [Хочу стать агентом]({})".format(AGENT_LINK), AGENT_LINK),
    ]
    missing = [line for line, url in links if url not in text]
    if missing:
        print(f"Model forgot links, adding: {len(missing)}")
        text = text.rstrip() + "\n" + "\n".join(missing)
    return text


def generate_image_url(topic, history):
    query = image_query_for(topic)
    used = {e.get("image_url") for e in history}
    if PEXELS_API_KEY:
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": PEXELS_API_KEY},
                params={"query": query, "per_page": 30},
                timeout=15,
            )
            photos = r.json().get("photos", [])
            candidates = [p["src"]["large"] for p in photos if p["src"]["large"] not in used]
            if not candidates:
                candidates = [p["src"]["large"] for p in photos]
            if candidates:
                url = random.choice(candidates)
                print(f"Image from Pexels: {url}")
                return url
        except Exception as e:
            print(f"Pexels error: {e}")
    keywords = query.replace(" ", ",")
    return f"https://loremflickr.com/1024/640/{keywords}?random={random.randint(1, 100000)}"

def generate_post(history):
    topic, content_type = pick_combo(history)
    print(f"Combo: type={content_type}, topic={topic}")
    news = fetch_news() if content_type in ("новость", "статистика") else None
    if content_type == "новость" and not news:
        content_type = "объяснение"

    client = OpenAI(api_key=API_KEY, base_url="https://api.groq.com/openai/v1")

    news_block = f"Новость/данные для поста: {news['title']}\n" if news else ""

    prompt = (
        "Ты юрист по списанию долгов и автор Telegram-канала. "
        "ГЛАВНЫЙ ТОН КАНАЛА: спокойствие и уверенность. Донеси, что банкротство — это "
        "законная, понятная и безопасная процедура, которую государство создало, чтобы помочь людям. "
        "Без паники и запугивания.\n"
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
            text = ensure_links(clean_thinking(response.choices[0].message.content))
            print(f"Groq answer ({model}): {text[:80]}...")
            return text, topic, content_type
        except Exception as e:
            print(f"Model {model} failed: {e}")

    fallback = (
        "💡 Важная информация о долгах\n\n"
        "Законодательство в сфере банкротства постоянно обновляется, защищая права должников.\n\n"
        f"💸 [Избавиться от долгов]({DEBT_LINK})\n"
        f"👉 [Пройти опрос]({AFFILIATE_LINK})\n"
        f"🤝 [Хочу стать агентом]({AGENT_LINK})"
    )
    return fallback, topic, content_type