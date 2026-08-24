# -*- coding: utf-8 -*-
import re
import requests

VK_API = "https://api.vk.com/method/"

def split_markdown(text):
    urls = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", text)
    clean = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", text)
    return clean, [u for _, u in urls]

def upload_photo(token, group_id, image_bytes):
    r = requests.get(VK_API + "photos.getWallUploadServer", params={
        "access_token": token, "group_id": group_id, "v": "5.131"
    }, timeout=30).json()
    if "error" in r:
        print(f"VK getWallUploadServer error: {r['error']}")
        return None
    upload_url = r["response"]["upload_url"]
    up = requests.post(upload_url, files={"photo": ("post.jpg", image_bytes, "image/jpeg")}, timeout=60).json()
    s = requests.get(VK_API + "photos.saveWallPhoto", params={
        "access_token": token, "v": "5.131",
        "photo": up["photo"], "server": up["server"], "hash": up["hash"]
    }, timeout=30).json()
    if "error" in s:
        print(f"VK saveWallPhoto error: {s['error']}")
        return None
    p = s["response"][0]
    return f"photo{p['owner_id']}_{p['id']}"

def vk_post(token, group_id, text, image_bytes=None):
    clean_text, urls = split_markdown(text)
    attachments = []
    if image_bytes:
        photo = upload_photo(token, group_id, image_bytes)
        if photo:
            attachments.append(photo)
    attachments.extend(urls)

    params = {
        "access_token": token,
        "v": "5.131",
        "owner_id": -int(group_id),
        "message": clean_text,
        "from_group": 1,
    }
    if attachments:
        params["attachments"] = ",".join(attachments)

    r = requests.post(VK_API + "wall.post", data=params, timeout=30).json()
    if "error" in r:
        print(f"VK error: {r['error']}")
        return False
    print(f"VK post ok: post_id={r['response']['post_id']}")
    return True