# -*- coding: utf-8 -*-
import sys, os, asyncio, base64

BASE = os.path.dirname(os.path.abspath(__file__))

def prepare_session():
    b64 = os.getenv("MAX_SESSION_B64", "")
    cache_dir = os.path.join(BASE, "cache")
    os.makedirs(cache_dir, exist_ok=True)
    path = os.path.join(cache_dir, "web.db")
    if not os.path.exists(path) and b64:
        with open(path, "wb") as f:
            f.write(base64.b64decode(b64))

def main():
    chat_id = int(sys.argv[1])
    text = sys.stdin.read()
    prepare_session()
    from pymax import WebClient
    client = WebClient(work_dir=os.path.join(BASE, "cache"), session_name="web.db")

    @client.on_start()
    async def on_start(c):
        try:
            await c.send_message(chat_id, text)
            print("MAX: message sent")
        finally:
            await c.stop()

    asyncio.run(client.start())
    os._exit(0)

main()