# -*- coding: utf-8 -*-
import subprocess, sys, os

def max_post(chat_id, text, image_url=None):
    if image_url:
        text = text + "\n\n📷 " + image_url
    script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "max_send.py")
    try:
        r = subprocess.run(
            [sys.executable, script, str(chat_id)],
            input=text, timeout=120, capture_output=True, text=True,
        )
        print("MAX:", (r.stdout or "").strip()[-300:])
        if r.returncode != 0:
            print("MAX stderr:", (r.stderr or "").strip()[-500:])
        return r.returncode == 0
    except Exception as e:
        print(f"MAX failed: {type(e).__name__}: {e}")
        return False