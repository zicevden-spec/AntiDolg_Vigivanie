import os
import random
from duckduckgo_search import DDGS
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

GROK_API_KEY = os.getenv("GROK_API_KEY")
AFFILIATE_LINK = os.getenv("AFFILIATE_LINK")

def search_news():
    queries = [
        "списание долгов физлиц 2025 2026 новости Россия",
        "банкротство через МФЦ изменения закон",
        "права должников коллекторы фз-230 новые поправки"
    ]
    query = random.choice(queries)
    
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=3)]
        if not results:
            return {"title": "Изменения в законах о долгах", "snippet": "Законодательство в сфере банкротства постоянно обновляется, следите за новостями.", "href": "https://fssp.gov.ru"}
        return random.choice(results)
    except Exception as e:
        print(f"Ошибка поиска DuckDuckGo: {e}")
        return {"title": "Важные новости о списании долгов", "snippet": "Следите за обновлениями в законодательстве РФ.", "href": "https://fssp.gov.ru"}

def generate_post():
    news = search_news()
    
    client = OpenAI(
        api_key=GROK_API_KEY,
        base_url="https://api.x.ai/v1"
    )
    
    prompt = f"""Ты — опытный юрист по списанию долгов и автор Telegram-канала. 
    Напиши короткий, полезный и цепляющий пост (до 1200 знаков) на основе этой новости:
    Заголовок: {news['title']}
    Суть: {news['snippet']}
    
    Правила:
    1. Объясни простыми словами, как это помогает должнику.
    2. Используй эмодзи для структуры (но не переборщи).
    3. В конце обязательно добавь призыв: "Узнайте, подходит ли вам списание долгов. Заполните бесплатную анкету за 1 минуту:"
    4. Сразу после призыва добавь ссылку на анкету: {AFFILIATE_LINK}
    5. В самом низу добавь строку: "Источник: {news['href']}"
    
    Не используй символы # и *, пиши обычным текстом с эмодзи.
    """
    
    try:
        response = client.chat.completions.create(
            model="grok-2-latest", 
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Ошибка генерации поста через Grok: {e}"
