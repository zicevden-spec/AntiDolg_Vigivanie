# -*- coding: utf-8 -*-
import sys, os, asyncio, base64, signal

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
    if len(sys.argv) < 2:
        print("MAX: no chat_id", file=sys.stderr)
        os._exit(1)
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
        except Exception as e:
            print(f"MAX send error: {type(e).__name__}: {e}", file=sys.stderr)
        # Жёсткий выход без await client.stop() — pymax вешает loop
        os._exit(0)

    try:
        asyncio.run(client.start())
    except Exception as e:
        print(f"MAX start error: {type(e).__name__}: {e}", file=sys.stderr)
    # Фолбэк если on_start не отстрелил
    os._exit(0)

main()