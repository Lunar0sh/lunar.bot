import discord
from discord.ext import commands, tasks
from discord import app_commands
import aiohttp
import os
import json
import datetime
import zoneinfo
import psutil
import time
import hashlib
import logging
from urllib.parse import urlparse
from dotenv import load_dotenv

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)-8s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("Lunar.Bot")

# Load Environment Variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
NASA_API_KEY = os.getenv("NASA_API_KEY")

# Constants
DEV_GUILD_ID = 1209920360565182506
DEV_GUILD = discord.Object(id=DEV_GUILD_ID)
OWNER_ID = 1390299961500897322
CONFIG_FILE = "config.json"
CACHE_FILE = "cache.json"
CACHE_DIR = "cached"
START_TIME = time.time()
DISCORD_FILE_LIMIT = 25 * 1024 * 1024  # 25 MB Limit for standard bots

# Design Constants
NASA_LOGO_URL = "https://cdn.freebiesupply.com/logos/large/2x/nasa-2-logo-png-transparent.png"
SPACE_COLORS = [0x0B3D91, 0x1B1B3A, 0x4B0082, 0x8A2BE2, 0xFF4500, 0xFFD700, 0x00CED1, 0x2F4F4F]

# Ensure cache directory exists
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)
    logger.info(f"Created cache directory: {CACHE_DIR}")


class APODBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=DEV_GUILD)
        await self.tree.sync(guild=DEV_GUILD)
        daily_apod_task.start()


bot = APODBot()


# --- Utility Functions ---

def load_json(filename):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


def get_daily_color():
    day_index = datetime.date.today().toordinal() % len(SPACE_COLORS)
    return SPACE_COLORS[day_index]


def cleanup_old_cache():
    """Löscht Dateien aus dem Cache, die älter als 7 Tage sind."""
    now = time.time()
    deleted_count = 0
    for filename in os.listdir(CACHE_DIR):
        filepath = os.path.join(CACHE_DIR, filename)
        if os.path.isfile(filepath):
            # Prüft das Erstellungs-/Änderungsdatum
            if os.stat(filepath).st_mtime < now - 7 * 86400:
                os.remove(filepath)
                deleted_count += 1
                logger.info(f"Deleted old cache file: {filename}")
    if deleted_count > 0:
        logger.info(f"Cleanup finished. Removed {deleted_count} old files.")


async def download_media(url: str, date_str: str) -> str | None:
    """Lädt das Bild/Video in den cached Ordner, sofern es nicht YouTube ist."""
    if "youtube.com" in url or "youtu.be" in url or "vimeo.com" in url:
        return None  # Externe Plattformen verarbeiten wir als Link

    parsed_url = urlparse(url)
    ext = os.path.splitext(parsed_url.path)[1]
    if not ext:
        ext = ".jpg"  # Fallback

    filepath = os.path.join(CACHE_DIR, f"{date_str}{ext}")

    if os.path.exists(filepath):
        logger.info(f"Serving media from cache: {filepath}")
        return filepath

    logger.info(f"Downloading new media from NASA: {url}")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    content_length = int(response.headers.get('Content-Length', 0))
                    if content_length > DISCORD_FILE_LIMIT:
                        logger.warning(f"File too large ({content_length} bytes). Skipping download.")
                        return None

                    data = await response.read()
                    if len(data) > DISCORD_FILE_LIMIT:
                        logger.warning("Downloaded data exceeds Discord limit. Discarding.")
                        return None

                    with open(filepath, 'wb') as f:
                        f.write(data)
                    logger.info(f"Successfully cached media to {filepath}")
                    return filepath
                else:
                    logger.error(f"Failed to download media. Status: {response.status}")
    except Exception as e:
        logger.error(f"Error downloading media: {e}")

    return None


async def fetch_apod_with_cache(params=None):
    is_standard_call = params is None or ("date" not in params and "count" not in params)

    if is_standard_call:
        cache = load_json(CACHE_FILE)
        today = datetime.date.today().isoformat()

        if cache.get("date") == today:
            logger.info("Serving APOD JSON data from cache.")
            return cache.get("data")

    url = "https://api.nasa.gov/planetary/apod"
    request_params = params.copy() if params else {}
    request_params['api_key'] = NASA_API_KEY

    logger.info(f"Fetching APOD JSON data from NASA API...")
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=request_params) as response:
            if response.status == 200:
                data = await response.json()

                if is_standard_call:
                    image_url = data.get("url", "")
                    url_hash = hashlib.md5(image_url.encode()).hexdigest()
                    save_json(CACHE_FILE, {
                        "date": datetime.date.today().isoformat(),
                        "url_hash": url_hash,
                        "data": data
                    })
                return data
            logger.error(f"NASA API returned status {response.status}")
            return None


class APODView(discord.ui.View):
    def __init__(self, hdurl: str = None, video_url: str = None):
        super().__init__()
        if hdurl:
            self.add_item(discord.ui.Button(label="View Full Resolution", url=hdurl, style=discord.ButtonStyle.link))
        if video_url:
            self.add_item(discord.ui.Button(label="Open Video Link", url=video_url, style=discord.ButtonStyle.link))


async def build_apod_message(data):
    if isinstance(data, list):
        data = data[0]

    title = data.get("title", "Astronomy Picture of the Day")
    desc = data.get("explanation", "No description available.")
    media_type = data.get("media_type")
    url = data.get("url")
    hdurl = data.get("hdurl")
    date = data.get("date", "Unknown Date")

    if len(desc) > 4000:
        desc = desc[:3997] + "..."

    embed = discord.Embed(title=title, description=desc, color=get_daily_color())
    embed.set_author(name="NASA API | APOD", icon_url=NASA_LOGO_URL)
    embed.set_footer(text=f"Date: {date} | Bot By Lunar_sh")

    content = None
    view = None
    file = None

    # Versuch, die Datei lokal zu cachen
    local_filepath = await download_media(url, date)

    if local_filepath:
        filename = os.path.basename(local_filepath)
        file = discord.File(local_filepath, filename=filename)

        if media_type == "image":
            embed.set_image(url=f"attachment://{filename}")
            view = APODView(hdurl=hdurl)
        elif media_type == "video":
            content = "**Today's APOD is a local video:**"
            view = APODView(video_url=url)
            # Bei Video setzen wir kein set_image. Das File wird normal gesendet und Discord baut den Player.

    else:
        # Fallback auf reines Verlinken, falls Datei zu groß oder YouTube Link
        logger.info("Serving APOD via direct URL links (Fallback or External Platform).")
        if media_type == "image":
            embed.set_image(url=url)
            view = APODView(hdurl=hdurl)
        elif media_type == "video":
            content = f"**Today's APOD is a video:**\n{url}"
            view = APODView(video_url=url)

    return content, embed, view, file


# --- Custom Checks ---

def is_owner():
    def predicate(interaction: discord.Interaction):
        if interaction.user.id != OWNER_ID:
            raise app_commands.CheckFailure("You do not have permission to use this command.")
        return True

    return app_commands.check(predicate)


# --- Commands ---

@bot.tree.command(name="apod", description="Fetches the current Astronomy Picture of the Day.")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def get_apod(interaction: discord.Interaction):
    await interaction.response.defer()
    logger.info(f"Command /apod executed by {interaction.user.name}")

    data = await fetch_apod_with_cache()
    if not data:
        await interaction.followup.send("Failed to reach NASA API.")
        return

    content, embed, view, file = await build_apod_message(data)

    kwargs = {"content": content, "embed": embed, "view": view}
    if file:
        kwargs["file"] = file

    await interaction.followup.send(**kwargs)


@bot.tree.command(name="random", description="Fetches a random APOD from the archives.")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def random_apod(interaction: discord.Interaction):
    await interaction.response.defer()
    logger.info(f"Command /random executed by {interaction.user.name}")

    data = await fetch_apod_with_cache(params={"count": 1})
    if not data:
        await interaction.followup.send("Failed to fetch random APOD.")
        return

    content, embed, view, file = await build_apod_message(data)

    kwargs = {"content": content, "embed": embed, "view": view}
    if file:
        kwargs["file"] = file

    await interaction.followup.send(**kwargs)


@bot.tree.command(name="apod_setup", description="Sets the daily drop channel (Server only).")
@app_commands.default_permissions(manage_channels=True)
async def setup_apod(interaction: discord.Interaction):
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used within a server.", ephemeral=True)
        return

    config = load_json(CONFIG_FILE)
    config["apod_channel"] = interaction.channel_id
    save_json(CONFIG_FILE, config)

    logger.info(f"Channel for daily drop set to {interaction.channel_id} in guild {interaction.guild.id}")
    await interaction.response.send_message(f"Daily APOD drops configured for {interaction.channel.mention}.",
                                            ephemeral=True)


@bot.tree.command(name="status", description="Displays system status (Owner only).")
@is_owner()
async def bot_status(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    cpu_usage = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory()
    ram_usage = f"{ram.used / (1024 ** 3):.2f}GB / {ram.total / (1024 ** 3):.2f}GB"

    embed = discord.Embed(title="System Status", color=get_daily_color())
    embed.set_author(name="Lunar.bot Diagnostics", icon_url=NASA_LOGO_URL)
    embed.add_field(name="Ping", value=f"`{latency} ms`", inline=True)
    embed.add_field(name="CPU", value=f"`{cpu_usage}%`", inline=True)
    embed.add_field(name="RAM", value=f"`{ram_usage}`", inline=False)

    # Calculate Cache Size
    cache_size = sum(os.path.getsize(os.path.join(CACHE_DIR, f)) for f in os.listdir(CACHE_DIR) if
                     os.path.isfile(os.path.join(CACHE_DIR, f)))
    cache_size_mb = cache_size / (1024 * 1024)
    embed.add_field(name="Local Cache Size", value=f"`{cache_size_mb:.2f} MB`", inline=False)

    embed.set_footer(text="Diagnostics | Bot By Lunar_sh")
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="nuke", description="Wipes all commands globally and across all servers.", guild=DEV_GUILD)
@is_owner()
async def nuke_commands(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    logger.info("Executing NUKE command...")
    bot.tree.clear_commands(guild=None)
    await bot.tree.sync(guild=None)
    for guild in bot.guilds:
        try:
            bot.tree.clear_commands(guild=guild)
            await bot.tree.sync(guild=guild)
        except:
            pass
    bot.tree.copy_global_to(guild=DEV_GUILD)
    await bot.tree.sync(guild=DEV_GUILD)
    logger.info("NUKE command finished.")
    await interaction.followup.send(content="Nuke complete. All old commands cleared.")


# --- Tasks ---

tz = zoneinfo.ZoneInfo("Europe/Berlin")
schedule_time = datetime.time(hour=8, minute=0, tzinfo=tz)


@tasks.loop(time=schedule_time)
async def daily_apod_task():
    logger.info("Running daily APOD task...")
    cleanup_old_cache()

    config = load_json(CONFIG_FILE)
    channel_id = config.get("apod_channel")

    if not channel_id:
        logger.warning("No daily channel configured.")
        return

    channel = bot.get_channel(channel_id)
    if not channel:
        logger.error(f"Configured channel {channel_id} not found.")
        return

    data = await fetch_apod_with_cache()
    if not data:
        logger.error("Failed to fetch data for daily drop.")
        return

    content, embed, view, file = await build_apod_message(data)

    kwargs = {"content": content, "embed": embed, "view": view}
    if file:
        kwargs["file"] = file

    await channel.send(**kwargs)
    logger.info(f"Daily APOD successfully dropped in channel {channel_id}.")


@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")
    logger.info(f"Connected to {len(bot.guilds)} guilds.")


bot.run(TOKEN)