# -*- coding: utf-8 -*-
import re
import requests

VK_API = "https://api.vk.com/method/"

def vk_text_from_markdown(text):
    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1: \2", text)

def upload_photo(token, group_id, image_bytes):
    r = requests.get(VK_API + "photos.getWallUploadServer", params={
        "access_token": token, "group_id": group_id, "v": "5.131"
    }, timeout=30).json()
    upload_url = r["response"]["upload_url"]
    up = requests.post(upload_url, files={"photo": ("post.jpg", image_bytes, "image/jpeg")}, timeout=60).json()
    s = requests.get(VK_API + "photos.saveWallPhoto", params={
        "access_token": token, "v": "5.131",
        "photo": up["photo"], "server": up["server"], "hash": up["hash"]
    }, timeout=30).json()
    p = s["response"][0]
    return f"photo{p['owner_id']}_{p['id']}"

def vk_post(token, group_id, text, image_bytes=None):
    message = vk_text_from_markdown(text)
    attachments = ""
    if image_bytes:
        try:
            attachments = upload_photo(token, group_id, image_bytes)
        except Exception as e:
            print(f"VK photo failed: {e}")
    r = requests.get(VK_API + "wall.post", params={
        "access_token": token,
        "v": "5.131",
        "owner_id": -int(group_id),
        "message": message,
        "attachments": attachments,
        "from_group": 1,
    }, timeout=30).json()
    if "error" in r:
        print(f"VK error: {r['error']}")
        return False
    print(f"VK post ok: post_id={r['response']['post_id']}")
    return True