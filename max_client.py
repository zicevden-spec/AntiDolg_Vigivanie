# -*- coding: utf-8 -*-
import asyncio
import base64
import os
import tempfile

def _decode_session_to_cache(b64: str) -> str:
    cache_dir = os.path.join(os.path.dirname(__file__), "cache")
    os.makedirs(cache_dir, exist_ok=True)
    path = os.path.join(cache_dir, "web.db")
    if os.path.exists(path):
        return path
    data = base64.b64decode(b64)
    with open(path, "wb") as f:
        f.write(data)
    return path

async def _send(chat_id: int, text: str, image_url: str | None = None):
    from pymax import WebClient
    session_b64 = os.getenv("MAX_SESSION_B64", "")
    if not session_b64:
        raise RuntimeError("MAX_SESSION_B64 is empty")
    _decode_session_to_cache(session_b64)
    client = WebClient(work_dir="cache", session_name="web.db")
    @client.on_start()
    async def on_start(c):
        try:
            if image_url:
                await c.send_message(chat_id, text, attachments=[{"type": "image", "url": image_url}])
            else:
                await c.send_message(chat_id, text)
        finally:
            await c.stop()
    await client.start()

def max_post(chat_id: str | int, text: str, image_url: str | None = None):
    try:
        asyncio.run(_send(int(chat_id), text, image_url))
        print(f"MAX: post sent to {chat_id}")
        return True
    except Exception as e:
        print(f"MAX failed: {type(e).__name__}: {e}")
        return False