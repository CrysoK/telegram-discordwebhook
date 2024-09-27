import logging
from os import environ
from typing import Optional
from discord import Bot, ApplicationContext, TextChannel
from discord.ext import tasks
from dotenv import load_dotenv
from telethon import TelegramClient, utils
from telethon.errors import SessionPasswordNeededError
from peewee import SqliteDatabase, DoesNotExist
from models import Config, Chat
from telegram import start


load_dotenv()

DISCORD_TOKEN = environ["DISCORD_TOKEN"]
DEBUG = bool(environ.get("DEBUG"))
DEBUG_GUILDS = [698632015162900522]
SESSION_NAME = "tg"
SQLITE_DB = "bot.db"

logging.basicConfig(
    format="[%(asctime)s %(levelname)s %(name)s] %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("main")
logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)

bot = Bot(debug_guilds=DEBUG_GUILDS if DEBUG else None)
tg: TelegramClient = None
db = SqliteDatabase(SQLITE_DB)
db.bind([Config, Chat])
last_code_hash = None


@tasks.loop()
async def start_telegram():
    global tg
    config = Config.get(id=0)
    try:
        tg = TelegramClient(SESSION_NAME, config.api_id, config.api_hash)
        await tg.connect()
        logger.info("Connected to Telegram")
        if await tg.is_user_authorized():
            logger.info("Logged in to Telegram")
            await start(tg, bot, db)
    except ValueError:
        logger.info("Not connected to Telegram")
        start_telegram.stop()


@start_telegram.before_loop
async def before_start_telegram():
    await bot.wait_until_ready()


@bot.event
async def on_ready():
    db.connect(reuse_if_open=True)
    db.create_tables([Config, Chat])
    Config.get_or_create(id=0)
    start_telegram.start()
    logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")
    db.close()


@bot.command()
async def ping(ctx):
    """Bot latency."""
    await ctx.respond(f"Pong! Latency: {bot.latency}")


@bot.command()
async def credentials(ctx: ApplicationContext, api_id: int, api_hash: str):
    """Set Telegram API credentials."""
    await ctx.defer(ephemeral=True)
    db.connect(reuse_if_open=True)
    config = Config.get(id=0)
    config.api_id = api_id
    config.api_hash = api_hash
    config.save()
    db.close()
    await ctx.respond("Credentials saved.", ephemeral=True)


@bot.command()
async def media_config(
    ctx: ApplicationContext,
    ibb_key: Optional[str],
    ibb_expiration: Optional[int],
    max_size: Optional[int],
):
    """Set media related options."""
    await ctx.defer(ephemeral=True)
    db.connect(reuse_if_open=True)
    config = Config.get(id=0)
    if ibb_key:
        config.ibb_key = ibb_key
    if ibb_expiration:
        config.ibb_expiration = ibb_expiration
    if max_size:
        config.max_size = max_size
    config.save()
    db.close()
    await ctx.respond("Media options saved.", ephemeral=True)


@bot.command()
async def add_chat(
    ctx: ApplicationContext,
    chat_id: int,
    channel: TextChannel,
    chat_name: Optional[str],
):
    """Add a chat to the list of monitored chats."""
    await ctx.defer(ephemeral=True)
    db.connect(reuse_if_open=True)
    logger.info(
        Chat.insert(
            id=chat_id, comment=chat_name, ignore_users=[], channels=[channel.id]
        )
    )
    db.close()
    await ctx.respond("Chat added.", ephemeral=True)


@bot.command()
async def list_chats(ctx: ApplicationContext):
    """List monitored chats."""
    await ctx.defer(ephemeral=True)
    db.connect(reuse_if_open=True)
    for t in db.get_tables():
        logger.info(t)
        logger.info([c.name for c in db.get_columns(t)])
        logger.info(db.execute_sql(f"SELECT * FROM {t}").fetchall())
    chats = list(Chat.select())
    db.close()
    await ctx.respond(f"{chats}", ephemeral=True)


@bot.command()
async def login(ctx: ApplicationContext, phone: str, login_code: Optional[str]):
    """Login to Telegram."""
    global tg
    await ctx.defer(ephemeral=True)
    config = Config.get(id=0)
    tg = TelegramClient(SESSION_NAME, config.api_id, config.api_hash)
    await tg.connect()
    if await tg.is_user_authorized():
        start_telegram.start()
        return await ctx.respond("Already logged in.", ephemeral=True)
    await tg.send_code_request(phone)
    if not login_code:
        return await ctx.respond("Rerun command with login code.", ephemeral=True)
    try:
        await tg.sign_in(phone, login_code)
    except ValueError as e:
        return await ctx.respond(f"```{e}```", ephemeral=True)
    except SessionPasswordNeededError:
        return await ctx.respond("2FA accounts are not supported.", ephemeral=True)
    if not await tg.is_user_authorized():
        return await ctx.respond("Login failed.", ephemeral=True)
    await ctx.respond("Login successful.", ephemeral=True)
    start_telegram.start()


@bot.command()
async def logout(ctx: ApplicationContext):
    """Logout from Telegram."""
    if not tg:
        await ctx.respond("Not logged in.", ephemeral=True)
        return
    start_telegram.stop()
    await tg.log_out()
    await ctx.respond("Logout successful.", ephemeral=True)


@bot.command()
async def status(ctx: ApplicationContext):
    """Telegram login status."""
    if not tg or not await tg.is_user_authorized():
        await ctx.respond("Not logged in.", ephemeral=True)
        return
    await ctx.respond("Logged in.", ephemeral=True)


@bot.command()
async def myself(ctx: ApplicationContext):
    """Get information about your Telegram account."""
    if not tg:
        await ctx.respond("Not logged in.", ephemeral=True)
        return
    await ctx.defer(ephemeral=True)
    me = await tg.get_me()
    await ctx.respond(f"```{me.stringify()}```", ephemeral=True)


@bot.command()
async def list_dialogs(ctx: ApplicationContext):
    if not await logged_in():
        await ctx.respond("Not logged in.", ephemeral=True)
        return
    dialogs = ""
    async for dialog in tg.iter_dialogs():
        dialogs += f"- {dialog.name} `{utils.resolve_id(dialog.id)[0]}`\n"
    await ctx.respond(dialogs, ephemeral=True)


async def logged_in():
    return tg and await tg.is_user_authorized()


bot.run(DISCORD_TOKEN)
