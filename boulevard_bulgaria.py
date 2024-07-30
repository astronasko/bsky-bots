from PIL import Image
import atproto
import feedparser
import json
import os
import requests

USER = "boulevardbulgaria.bsky.social"
PASS = os.environ["BB_PASS"]
BSKY_CLIENT = atproto.Client()
BSKY_CLIENT.login(USER, PASS)
CACHE_FILENAME = "cache/boulevard_bulgaria.json"

# Load cache
with open(CACHE_FILENAME, "r") as file:
    cache = json.load(file)
    etag = cache["etag"]
    entry_ids = cache["entry_ids"]

feed_dict = feedparser.parse(
    "https://boulevardbulgaria.bg/feed.atom",
    etag=etag,
)
cache["etag"] = feed_dict.etag

for entry in feed_dict.entries:
    if entry.id not in entry_ids:
        entry_link = entry.link
        entry_thumb = entry.media_content[0]["url"]
        entry_title = entry.title
        while len(entry_title)>150:
            entry_title = " ".join(entry_title.split(" ")[:-1])
            entry_title += ".."
        
        entry_image = Image.open(
            fp=requests.get(
                url=entry_thumb,
                stream=True
            ).raw
        )
        if entry_image.size[0] > 1280:
            scale = 1280/entry_image.size[0]
            entry_image = entry_image.resize(
                size=[int(x*scale) for x in entry_image.size],
            )

        text_builder = atproto.client_utils.TextBuilder()
        text_builder.text(f"{entry_title}. ")
        text_builder.link("линк", entry_link)
        BSKY_CLIENT.send_image(
            text=text_builder,
            image=entry_image.tobytes(),
            image_alt="",
            langs=["bg"]
        )
        cache["entry_ids"].append(entry.id)

cache_len = len(cache["entry_ids"])
if cache_len > 1000:
    cache["entry_ids"] = cache["entry_ids"][cache_len-1000:]

with open(CACHE_FILENAME, "w") as file:
    json.dump(cache, file, indent=4)
