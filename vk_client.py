# -*- coding: utf-8 -*-
import re
import requests

VK_API = "https://api.vk.com/method/"

def split_markdown(text):
    pairs = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", text)
    clean = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", text)
    return clean, pairs

def try_upload_wall_photo(token, image_bytes, extra):
    s = requests.post(VK_API + "photos.getWallUploadServer", data={
        "access_token": token, "v": "5.131", **extra
    }, timeout=30).json()
    if "error" in s:
        print(f"VK upload server {extra or 'default'} denied: {s['error'].get('error_code')}")
        return None
    up = requests.post(
        s["response"]["upload_url"],
        files={"photo": ("post.jpg", image_bytes, "image/jpeg")},
        timeout=60,
    ).json()
    sv = requests.post(VK_API + "photos.saveWallPhoto", data={
        "access_token": token, "v": "5.131",
        "server": up["server"], "photo": up["photo"], "hash": up["hash"],
    }, timeout=30).json()
    if "error" in sv:
        print(f"VK saveWallPhoto denied: {sv['error'].get('error_code')}")
        return None
    p = sv["response"][0]
    print("VK photo uploaded!")
    return f"photo{p['owner_id']}_{p['id']}"

def upload_photo(token, group_id, image_bytes):
    return (
        try_upload_wall_photo(token, image_bytes, {})
        or try_upload_wall_photo(token, image_bytes, {"group_id": group_id})
    )

def vk_post(token, group_id, text, image_bytes=None):
    clean_text, pairs = split_markdown(text)
    photo = upload_photo(token, group_id, image_bytes) if image_bytes else None

    attachments = []
    if photo:
        attachments.append(photo)

    if photo and pairs:
        attachments.append(pairs[0][1])
        body = clean_text
    else:
        body = clean_text
        if pairs:
            body += "\n\n" + "\n".join(f"{label}: {url}" for label, url in pairs)

    params = {
        "access_token": token,
        "v": "5.131",
        "owner_id": -int(group_id),
        "message": body,
        "from_group": 1,
    }
    if attachments:
        params["attachments"] = ",".join(attachments)

    r = requests.post(VK_API + "wall.post", data=params, timeout=30).json()
    if "error" in r:
        print(f"VK error: {r['error']}")
        return False
    post_id = r["response"]["post_id"]
    print(f"VK post ok: post_id={post_id}")

    if photo and len(pairs) > 1:
        comment = "\n".join(f"{label}: {url}" for label, url in pairs[1:])
        c = requests.post(VK_API + "wall.createComment", data={
            "access_token": token, "v": "5.131",
            "owner_id": -int(group_id),
            "post_id": post_id,
            "message": comment,
            "from_group": 1,
        }, timeout=30).json()
        print("VK comment ok" if "response" in c else f"VK comment error: {c.get('error')}")
    return True