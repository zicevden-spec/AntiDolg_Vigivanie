import asyncio
from pymax import Client

# ЗАМЕНИ на свой номер MAX (с +7, без пробелов)
PHONE = "+79789784260"

client = Client(phone=PHONE, work_dir="cache", session_name="main.db")

@client.on_start()
async def on_start(client):
    print("✓ Клиент запущен!")
    print("Ваш ID:", client.me.contact.id if client.me else "?")
    try:
        await client.send_message(-78194194926917, "🤝 Тестовый пост от автопостера АнтиДолг. Если видишь это — MAX подключён!")
        print("✓ Пост отправлен в канал!")
    except Exception as e:
        print(f"✗ Ошибка отправки: {type(e).__name__}: {e}")
    finally:
        await client.stop()

asyncio.run(client.start())