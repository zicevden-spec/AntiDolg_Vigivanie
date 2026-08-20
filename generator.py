# -*- coding: utf-8 -*-
import os
import random
import requests
from bs4 import BeautifulSoup
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
        url = f"https://html.duckduckgo.com/html/?q={query}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=10)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        results = soup.find_all('div', class_='result__body')
        
        if results:
            result = random.choice(results[:3])
            title = result.find('a', class_='result__snippet')
            link = result.find('a', class_='result__url')
            
            return {
                "title": title.text.strip() if title else "Новые правила по долгам",
                "snippet": title.text.strip() if title else "Законодательство обновляется",
                "href": link.get('href') if link else "https://fssp.gov.ru"
            }
    except Exception as e:
        print(f"Ошибка поиска: {e}")
    
    return {
        "title": "Важные изменения в законах о долгах",
        "snippet": "Законодательство в сфере банкротства постоянно обновляется, защищая права должников.",
        "href": "https://fssp.gov.ru"
    }

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
    2. Используй эмодзи для структуры.
    3. В конце обязательно добавь призыв: "Узнайте, подходит ли вам списание долга. Заполните бесплатную анкету за 1 минуту:"
    4. Сразу после призыва добавь ссылку на анкету: {AFFILIATE_LINK}
    5. В самом низу добавь строку: "Источник: {news['href']}"
    
    Не используй символы # и *, пиши обычным текстом с эмодзи.
    """
    
    try:
        response = client.chat.completions.create(
            model="grok-3-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7, max_tokens=600
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Ошибка генерации: {e}")
        return f"Важная информация о долгах\n\n{news['snippet']}\n\nУзнайте, подходит ли вам списание долга:\n{AFFILIATE_LINK}\n\nИсточник: {news['href']}"
