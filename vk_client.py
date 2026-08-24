# -*- coding: utf-8 -*-
import re
import requests

VK_API = "https://api.vk.com/method/"

def split_markdown(text):
    pairs = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", text)
    clean = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", text)
    return clean, pairs

def get_or_create_album(token, group_id):
    r = requests.post(VK_API + "photos.getAlbums", data={
        "access_token": token, "v": "5.131", "group_id": group_id,
    }, timeout=30).json()
    if "error" in r:
        print(f"VK getAlbums error: {r['error']}")
        return None
    for a in r["response"]["items"]:
        if a["title"] == "Посты":
            return a["id"]
    c = requests.post(VK_API + "photos.createAlbum", data={
        "access_token": token, "v": "5.131", "group_id": group_id, "title": "Посты",
    }, timeout=30).json()
    if "error" in c:
        print(f"VK createAlbum error: {c['error']}")
        return None
    return c["response"]["id"]

def upload_photo(token, group_id, image_bytes):
    album_id = get_or_create_album(token, group_id)
    if not album_id:
        return None
    s = requests.post(VK_API + "photos.getUploadServer", data={
        "access_token": token, "v": "5.131",
        "group_id": group_id, "album_id": album_id,
    }, timeout=30).json()
    if "error" in s:
        print(f"VK getUploadServer error: {s['error']}")
        return None
    up = requests.post(
        s["response"]["upload_url"],
        files={"file1": ("post.jpg", image_bytes, "image/jpeg")},
        timeout=60,
    ).json()
    sv = requests.post(VK_API + "photos.savePhotos", data={
        "access_token": token, "v": "5.131",
        "group_id": group_id, "album_id": album_id,
        "server": up["server"], "photos_list": up["photos_list"], "hash": up["hash"],
    }, timeout=30).json()
    if "error" in sv:
        print(f"VK savePhotos error: {sv['error']}")
        return None
    p = sv["response"][0]
    return f"photo{p['owner_id']}_{p['id']}"

def vk_post(token, group_id, text, image_bytes=None):
    clean_text, pairs = split_markdown(text)

    attachments = []
    if image_bytes:
        photo = upload_photo(token, group_id, image_bytes)
        if photo:
            attachments.append(photo)
    if pairs:
        attachments.append(pairs[0][1])

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
    post_id = r["response"]["post_id"]
    print(f"VK post ok: post_id={post_id}")

    if len(pairs) > 1:
        comment = "\n".join(f"{label}: {url}" for label, url in pairs[1:])
        c = requests.post(VK_API + "wall.createComment", data={
            "access_token": token, "v": "5.131",
            "owner_id": -int(group_id),
            "post_id": post_id,
            "message": comment,
            "from_group": 1,
        }, timeout=30).json()
        if "error" in c:
            print(f"VK comment error: {c['error']}")
        else:
            print("VK comment ok")
    return True