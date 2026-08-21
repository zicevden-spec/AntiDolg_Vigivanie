# -*- coding: utf-8 -*-
import os
import random
import re
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
]

WORKING_MODELS = [
    "openai/gpt-oss-120b",
    "groq/compound",
    "qwen/qwen3.6-27b",
]

def clean_thinking(text):
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()

def generate_post():
    topic = random.choice(TOPICS)
    client = OpenAI(api_key=API_KEY, base_url="https://api.groq.com/openai/v1")

    prompt = (
        "Ты юрист по списанию долгов и автор Telegram-канала. "
        f"Напиши короткий, полезный пост (до 900 знаков) на тему: {topic}. "
        "Правила:\n"
        "1. Пиши простыми словами, используй эмодзи для структуры.\n"
        "2. НЕ используй символы # и *.\n"
        "3. В самом конце поста добавь РОВНО 3 строки:\n"
        f"💸 [Избавиться от долгов]({DEBT_LINK})\n"
        f"👉 [Пройти опрос]({AFFILIATE_LINK})\n"
        f"🤝 [Хочу стать агентом]({AGENT_LINK})\n"
        "4. После этих трёх строк НИЧЕГО больше не пиши.\n"
        "5. НЕ показывай процесс рассуждения, только финальный пост.\n"
    )

    for model in WORKING_MODELS:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000,
            )
            text = clean_thinking(response.choices[0].message.content)
            print(f"Groq answer ({model}): {text[:100]}...")
            return text
        except Exception as e:
            print(f"Model {model} failed: {e}")

    return (
        "💡 Важная информация о долгах\n\n"
        "Законодательство в сфере банкротства постоянно обновляется, защищая права должников.\n\n"
        f"💸 [Избавиться от долгов]({DEBT_LINK})\n"
        f"👉 [Пройти опрос]({AFFILIATE_LINK})\n"
        f"🤝 [Хочу стать агентом]({AGENT_LINK})"
    )