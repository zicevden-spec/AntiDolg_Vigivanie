import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("GROK_API_KEY")
print(f"Key length: {len(key) if key else 0}")
print(f"Key starts with: {key[:10] if key else 'None'}...")

client = OpenAI(api_key=key, base_url="https://api.groq.com/openai/v1")

try:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": "Привет, скажи одно слово"}],
        max_tokens=50
    )
    print(f"SUCCESS: {response.choices[0].message.content}")
except Exception as e:
    print(f"ERROR: {e}")