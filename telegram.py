import logging
import json
import aiohttp
from discord import Bot
from telethon import TelegramClient, events, utils, types
from telethon.extensions import markdown
from peewee import SqliteDatabase
from models import Chat, Config

logger = logging.getLogger(__name__)


class MarkdownNoEmbeds:
    @staticmethod
    def parse(text):
        return markdown.parse(text)

    @staticmethod
    def unparse(text, entities):
        """Convierte `https://example.com` a `<https://example.com>` y
        `[example](https://example.com)` a `[example](<https://example.com>)`
        """
        new_text = list(text)
        offset_correction = 0
        for e in entities or []:
            if isinstance(e, types.MessageEntityUrl):
                start = e.offset + offset_correction
                end = start + e.length
                new_text.insert(start, "<")
                new_text.insert(end + 1, ">")
                offset_correction += 2
                e.length = e.length + 2
                e.offset = start
            if isinstance(e, types.MessageEntityTextUrl):
                e.url = f"<{e.url}>"
        return markdown.unparse("".join(new_text), entities)


async def start(client: TelegramClient, bot: Bot, db: SqliteDatabase):
    db.connect(reuse_if_open=True)
    config = Config.get(id=0)
    ibb_key = config.ibb_key
    ibb_expiration = config.ibb_expiration
    max_size = config.max_size
    chats_ids = Chat.select(Chat.id)
    db.close()

    # chats_ids = list(map(int, keys)) if "*" not in (keys := CHATS.keys()) else None

    client.parse_mode = MarkdownNoEmbeds()  # ¿Hacerlo opcional? ¿Por cada Chat?
    session = aiohttp.ClientSession()

    @client.on(events.NewMessage(chats=chats_ids))
    async def new_message(event: events.NewMessage.Event):
        chat = await event.get_chat()
        sender = await event.get_sender()
        try:
            config = Chat.get(id=utils.resolve_id(chat))
            targets = config.channels
        except KeyError as e:
            logger.error(f"Missing required field '{e.args[0]}' in config.json")
            return
        ignore_usernames = config.get("ignore_users", [])
        if sender.username in ignore_usernames:
            logger.info(f"User @{sender.username} ignored")
            return
        author = f" @{sender.username}" if sender.username else ""
        d_username = utils.get_display_name(chat) + author
        data = {
            "username": d_username,
            "content": event.text,
        }
        if ibb_key:
            data["avatar_url"] = await get_profile_photo_url(chat)
        if event.message.file:
            filename = event.message.file.name or f"file.{event.message.file.ext}"
            if event.message.file.size <= max_size:
                blob = await event.message.download_media(bytes)
                data[filename] = blob
            else:
                logger.warning(
                    f"File {filename} exceeds maximum size of {max_size / 1024 / 1024} MB"
                )
        for target in targets:
            try:
                await bot.get_channel(target).send(**data)
                logger.info(f"Forwarded message from {d_username}")
            except Exception:
                logger.error(f"Error forwarding message from {d_username}")

    def load_cache() -> dict:
        cache = {}
        try:
            with open("cache.json") as f:
                try:
                    cache = json.load(f)
                except json.JSONDecodeError as e:
                    # ¿abortar o sobrescribir?
                    while opt := input(
                        "cache.json corrupted. Overwrite? (y/n): "
                    ).lower():
                        if opt == "y":
                            break
                        elif opt == "n":
                            raise e
        except FileNotFoundError:
            logger.info("cache.json not found")
        return cache

    async def get_profile_photo_url(entity):
        if not hasattr(entity.photo, "photo_id"):
            return ""
        filename = f"{entity.id}-{entity.photo.photo_id}.jpg"
        cache = load_cache()
        code = cache.get(filename, "0")
        url = f"https://i.ibb.co/{code}/{filename}"
        async with session.get(url) as r1:
            if r1.status == 200:
                return url
            logger.info(f"Cache miss: {filename}")
            data = {
                "key": ibb_key,
                "name": filename,
                "expiration": str(ibb_expiration),
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

    try:
        await client.catch_up()
        # async for chat in client.iter_dialogs():
        #     print(f"Chat: {chat.name} ID: {utils.resolve_id(chat.id)[0]}")
        await client.run_until_disconnected()
    finally:
        await session.close()
