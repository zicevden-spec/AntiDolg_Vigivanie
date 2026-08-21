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
        f"Напиши короткий пост (до 900 знаков) на тему: {topic}. "
        "Правила: пиши простыми словами, используй эмодзи, "
        "без символов # и *. В конце добавь призыв: "
        "'Узнайте, подходит ли вам списание долга. Заполните бесплатную анкету за 1 минуту:' "
        f"и ссылку {AFFILIATE_LINK}. "
        "Ничего больше после ссылки не пиши."
    )

    try:
        response = client.chat.completions.create(
            model="grok-3-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=600,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Ошибка генерации: {e}")
        return (
            "Важная информация о долгах\n\n"
            "Законодательство в сфере банкротства постоянно обновляется, защищая права должников.\n\n"
            "Узнайте, подходит ли вам списание долга:\n"
            f"{AFFILIATE_LINK}"
        )