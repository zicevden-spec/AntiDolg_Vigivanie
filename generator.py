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
    "банкротство при разводе супругов",
    "банкротство с долгом в иностранной валюте",
    "банкротство при долгах перед родственниками",
    "банкротство после продажи имущества",
    "банкротство с действующим исполнительным производством",
    "чек-лист: готов ли ты к банкротству",
    "как собрать доказательства неплатежеспособности",
    "что делать если отказали в банкротстве",
    "как проверить арбитражного управляющего",
    "реальные истории людей после банкротства",
    "как объяснить банкротство детям",
    "как пережить давление родственников",
    "почему стыдно просить о банкротстве",
    "кредит на банкротство - почему это ловушка",
    "что делать если юрист пропал с деньгами",
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
    two_days = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=2)
    out = []
    for e in history:
        try:
            if datetime.datetime.fromisoformat(e["ts"]) >= two_days:
                out.append(e)
        except Exception:
            pass
    return out


def pick_combo(history):
    now = datetime.datetime.now(datetime.timezone.utc)
    day_ago = now - datetime.timedelta(hours=24)
    two_days_ago = now - datetime.timedelta(days=2)
    topics_today = {e["topic"] for e in history if datetime.datetime.fromisoformat(e["ts"]) >= day_ago}
    recent_pairs = {(e["topic"], e["type"]) for e in history if datetime.datetime.fromisoformat(e["ts"]) >= two_days_ago}
    candidates = [(t, c) for t in TOPICS for c in CONTENT_TYPES if t not in topics_today and (t, c) not in recent_pairs]
    if not candidates:
        candidates = [(t, c) for t in TOPICS for c in CONTENT_TYPES if (t, c) not in recent_pairs]
    if not candidates:
        candidates = [(t, c) for t in TOPICS for c in CONTENT_TYPES]
    print(f"Candidates pool: {len(candidates)}")
    return random.choice(candidates)



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

def normalize_links(text, max_len=None):
    bad_markers = [DEBT_LINK, AFFILIATE_LINK, AGENT_LINK,
                   "Избавиться от долгов", "Пройти опрос", "Хочу стать агентом"]
    clean_lines = []
    for line in text.split("\n"):
        s = line.strip()
        if not s:
            continue
        if any(m in s for m in bad_markers):
            continue
        if "http" in s and ("[" in s or "(" in s or "xn--" in s):
            continue
        if re.match(r"^[\W_]+$", s):
            continue
        clean_lines.append(line)
    text = "\n".join(clean_lines)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if max_len and len(text) > max_len:
        budget = max_len
        cut = text[:budget]
        idx = cut.rfind("\n\n")
        if idx < budget * 0.5:
            idx = cut.rfind("\n")
        if idx > budget * 0.5:
            cut = cut[:idx]
        text = cut.rstrip()
        print(f"Truncated to {max_len}")
    return text


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
            text = normalize_links(clean_thinking(response.choices[0].message.content))
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
def ensure_dzen_links(text):
    pairs = [
        ("Избавиться от долгов", DEBT_LINK),
        ("Пройти опрос", AFFILIATE_LINK),
        ("Хочу стать агентом", AGENT_LINK),
    ]
    missing = [f"{label}: {url}" for label, url in pairs if url not in text]
    if missing:
        text = text.rstrip() + "\n" + "\n".join(missing)
    return text


def generate_dzen_article():
    client = OpenAI(api_key=API_KEY, base_url="https://api.groq.com/openai/v1")
    attempts = 0
    while attempts < 3:
        topic = random.choice(TOPICS)
        prompt = (
            "Ты опытный юрист по банкротству физлиц с 15-летним стажем. "
            "Твоя задача — писать образовательные статьи, которые помогают обычным людям разобраться в законных процедурах избавления от долгов. "
            "Это официальный государственный механизм помощи гражданам, абсолютно легальный и безопасный. "
            f"Напиши подробную статью на тему: {topic}. "
            "Формат статьи:\n"
            "1. Первая строка — цепляющий заголовок (без символа #).\n"
            "2. Затем пустая строка и основной текст МИНИМУМ 3000 и МАКСИМУМ 3600 знаков. Меньше 3000 — слишком коротко, распиши каждый раздел подробнее. Структура, при которой мысль полностью закончена в лимите: вступление (около 300 знаков), 3 раздела (около 900 знаков каждый), вывод (около 400 знаков). Пиши компактно, без воды и повторов. Если чувствуешь, что не помещаешься — не начинай новую мысль, а сожми последний раздел и обязательно заверши законченным выводом.\n"
            "3. Раздели текст на 3-4 смысловых блока с короткими подзаголовками (обычным текстом, без # и * и без КАПСЛОКА).\n"
            "4. В конце — органичный вывод (2-3 предложения), который естественно завершает мысль. ЗАПРЕЩЕНО использовать шаблонные заголовки типа 'ВЫВОД', 'ПРАКТИЧЕСКИЙ ВЫВОД', 'ИТОГ', 'ПРИЗЫВ К ДЕЙСТВИЮ' и подобные — просто пиши связный заключительный абзац.\n"
            "5. Тон: спокойный, уверенный, экспертный. Банкротство — это законный инструмент помощи, не катастрофа.\n"
            "6. В самом конце добавь три строки с обычными ссылками (без Markdown):\n"
            f"Избавиться от долгов: {DEBT_LINK}\n"
            f"Пройти опрос: {AFFILIATE_LINK}\n"
            f"Хочу стать агентом: {AGENT_LINK}\n"
            "7. НЕ показывай рассуждения, только готовую статью.\n"
            "ФОРМАТ ОФОРМЛЕНИЯ: разбивай статью на разделы с подзаголовками и эмодзи (например: ⚖️ 💡 📌  🔹). Каждый подзаголовок — с новой строки. Между абзацами — пустая строка. Абзацы короткие, 3-4 предложения. Где уместно — используй списки с эмодзи-маркерами (✅ ❌ 🔸). Начни статью с короткой живой истории или вопроса к читателю, закончи тёплым выводом.\n"
            "8. ВАЖНО: тело статьи строго до 3600 знаков. Законченная мысль важнее длины — никогда не обрывай текст на полуслове.\n"
        )
        for model in WORKING_MODELS:
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.8,
                    max_tokens=4096,
                )
                raw = clean_thinking(response.choices[0].message.content)
                if ("I'm sorry" in raw or "I can't" in raw or "I cannot" in raw or "не могу" in raw or "извините" in raw or len(raw) < 500):
                    print(f"Dzen: model refused topic '{topic}', retrying")
                    break
                text = normalize_links(raw, 4050)
                print(f"Dzen article ready ({model}), topic: {topic}")
                return text, topic
            except Exception as e:
                print(f"Dzen model {model} failed: {e}")
        attempts += 1
    print("Dzen: all attempts failed")
    return None



def format_readable(text):
    # Разбиваем сплошной текст на абзацы: пустая строка после точки перед эмодзи-маркером
    text = re.sub(r'(?<=[.!?])\s+(?=[\u2600-\u27BF\U0001F000-\U0001FAFF])', '\n\n', text)
    return text.strip()