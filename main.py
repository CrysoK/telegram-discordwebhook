# python 3.8+
import argparse
import logging
import json
import aiohttp
from telethon import TelegramClient, events, utils

logging.basicConfig(
    format="[%(levelname)8s|%(asctime)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("main")

with open("config.json") as f:
    CONFIG = json.load(f)

API_ID = int(CONFIG["api_id"])
API_HASH = str(CONFIG["api_hash"])
IBB_KEY = str(CONFIG["ibb_key"])
MAX_SIZE = int(CONFIG["max_size"]) * 1024 * 1024
PPHOTO_EXPIRATION = int(CONFIG["pphoto_expiration"]) * 24 * 60 * 60
WEBHOOKS: dict = CONFIG["webhooks"]
CHATS = list(map(int, keys)) if "*" not in (keys := WEBHOOKS.keys()) else None

client = TelegramClient("anon", API_ID, API_HASH)
session = None


@client.on(events.NewMessage(chats=CHATS))
async def new_message(event: events.NewMessage.Event):
    chat = await event.get_chat()
    sender = await event.get_sender()
    target = WEBHOOKS.get(str(chat.id)) or WEBHOOKS.get("*")
    if target:
        author = f" @{sender.username}" if sender.username else ""
        data = {
            "username": utils.get_display_name(chat) + author,
            "content": f"{event.text}",
        }
        if IBB_KEY:
            data["avatar_url"] = await get_profile_photo_url(chat)
        if event.message.file:
            filename = event.message.file.name or f"file.{event.message.file.ext}"
            if event.message.file.size <= MAX_SIZE:
                blob = await event.message.download_media(bytes)
                data[filename] = blob
            else:
                logger.warning(
                    f"File {filename} exceeds maximum size of {MAX_SIZE / 1024 / 1024} MB"
                )
        async with session.post(target, data=data) as r:
            if r.status in (200, 204):
                logger.info("Forwarded message")
            else:
                logger.error(f"Failed to forward message ({r.status})")


async def get_profile_photo_url(entity):
    if not hasattr(entity.photo, "photo_id"):
        return ""
    filename = f"{entity.id}-{entity.photo.photo_id}.jpg"
    try:
        with open("cache.json") as f:
            try:
                cache = json.load(f)
            except json.JSONDecodeError as e:
                # ¿abortar o sobrescribir?
                while opt := input("cache.json corrupted. Overwrite? [y/n]: ").lower():
                    if opt == "y":
                        cache = {}
                        break
                    elif opt == "n":
                        raise e
    except FileNotFoundError as e:
        logger.info("cache.json not found")
        cache = {}
    code = cache.get(filename, "0")
    url = f"https://i.ibb.co/{code}/{filename}"
    async with session.get(url) as r1:
        if r1.status == 200:
            return url
        logger.info(f"Cache miss: {filename}")
        data = {
            "key": IBB_KEY,
            "name": filename,
            "expiration": str(PPHOTO_EXPIRATION),
            "image": await client.download_profile_photo(entity, bytes),
        }
        async with session.post("https://api.imgbb.com/1/upload", data=data) as r2:
            if r2.status == 200:
                info = (await r2.json())["data"]
                url = info["url"]
                code = url.split("/")[3]
                cache[filename] = code
                with open("cache.json", "w") as f:
                    json.dump(cache, f, indent=2)
                return url
            logger.error(f"Failed to upload image ({r2.status})")
    return ""


async def main(args):
    await client.catch_up()
    global session
    session = aiohttp.ClientSession()
    if args.list:
        async for chat in client.iter_dialogs():
            print(f"Chat: {chat.name} ID: {utils.resolve_id(chat.id)[0]}")
    else:
        await client.run_until_disconnected()
    await session.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--list", action="store_true", help="List chats IDs")
    args = parser.parse_args()
    try:
        with client:
            client.loop.run_until_complete(main(args))
    except KeyboardInterrupt:
        pass
