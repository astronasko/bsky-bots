from PIL import Image
import atproto
import atproto.exceptions
import feedparser
import json
import os
import requests
import io

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

for entry in feed_dict.entries[::-1]:
    if entry.id not in entry_ids:
        entry_link = entry.link
        try:
            entry_thumb = entry.media_content[0]["url"]
        except AttributeError:
            entry_thumb = "thumbnails/boulevard_bulgaria.jpg"
        entry_title = entry.title
        while len(entry_title)>150:
            entry_title = " ".join(entry_title.split(" ")[:-1])
            entry_title += ".."
        
        entry_image = Image.open(
            fp=requests.get(
                url=entry_thumb,
                stream=True
            ).raw
        ).convert("RGB")
        entry_image.thumbnail(
            size=(640,360),
        )
        entry_image_quality = 90
        post_response = None

        while post_response is None:
            try:
                entry_image_bytes = io.BytesIO()
                entry_image.save(
                    entry_image_bytes,
                    "JPEG",
                    optimize=True,
                    quality=90
                )
                embed_external = atproto.models.AppBskyEmbedExternal.Main(
                    external=atproto.models.AppBskyEmbedExternal.External(
                        title=entry_title,
                        description="",
                        uri=entry_link,
                        thumb=BSKY_CLIENT.upload_blob(entry_image_bytes.getvalue()).blob
                    )
                )
                post_response = BSKY_CLIENT.send_post(
                    text=f"{entry_title}.",
                    embed=embed_external,
                    langs=["bg"]
                )
            except atproto.exceptions.BadRequestError:
                entry_image_quality -= 10
            if entry_image_quality < 40:
                # Fall back to a default thumbnail
                entry_image = Image.open(
                    fp="thumbnails/boulevard_bulgaria.jpg"
                )
                entry_image_quality = 90
                
        cache["entry_ids"].append(entry.id)

cache_len = len(cache["entry_ids"])
if cache_len > 1000:
    cache["entry_ids"] = cache["entry_ids"][cache_len-1000:]

with open(CACHE_FILENAME, "w") as file:
    json.dump(cache, file, indent=4)
