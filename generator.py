# -*- coding: utf-8 -*-
import os
import random
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

GROK_API_KEY = os.getenv("GROK_API_KEY")
AFFILIATE_LINK = os.getenv("AFFILIATE_LINK")

TOPICS = [
    "списание долгов через банкротство физлиц",
    "права должников при звонках коллекторов",
    "банкротство через МФЦ без суда",
    "что не могут забрать коллекторы у должника",
]

def generate_post():
    topic = random.choice(TOPICS)
    client = OpenAI(api_key=GROK_API_KEY, base_url="https://api.x.ai/v1")

    prompt = (
        "Ты юрист по списанию долгов и автор Telegram-канала. "
        f"Напиши короткий, полезный пост (до 900 знаков) на тему: {topic}. "
        "Правила:\n"
        "1. Пиши простыми словами, используй эмодзи для структуры.\n"
        "2. НЕ используй символы # и *, кроме одного Markdown-ссылки в конце.\n"
        "3. В самом конце поста (после основного текста) добавь ОДНУ строку:\n"
        f"👉 [Избавиться от долгов]({AFFILIATE_LINK})\n"
        "4. После этой строки НИЧЕГО больше не пиши — никаких 'Источник', 'P.S.', прощаний.\n"
    )

    try:
        response = client.chat.completions.create(
            model="grok-3-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=600,
        )
        text = response.choices[0].message.content
        print(f"Grok answer: {text[:200]}...")
        return text
    except Exception as e:
        print(f"Ошибка генерации: {e}")
        return (
            "💡 Важная информация о долгах\n\n"
            "Законодательство в сфере банкротства постоянно обновляется, защищая права должников.\n\n"
            f"👉 [Избавиться от долгов]({AFFILIATE_LINK})"
        )