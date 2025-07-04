# bot.py
import os
import json
import requests
import discord
from discord.ext import commands, tasks
from discord import app_commands
from dotenv import load_dotenv
from datetime import time, date
import io
from PIL import Image  # <-- New library for image processing. Run: pip install Pillow

# --- SETUP ---

# Load environment variables from a .env file
# Create a file named .env in the same directory and add your keys:
# DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN
# NASA_API_KEY=YOUR_NASA_API_KEY
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
NASA_API_KEY = os.getenv('NASA_API_KEY')

# Check if tokens are loaded
if not DISCORD_TOKEN or not NASA_API_KEY:
    print("Error: DISCORD_TOKEN or NASA_API_KEY not found in .env file.")
    print("Please create a .env file and add your tokens.")
    exit()

# --- DIRECTORY SETUP ---
# Create folders for caching images if they don't exist
os.makedirs('cached_raw', exist_ok=True)
os.makedirs('cache', exist_ok=True)

# Define the intents for the bot
intents = discord.Intents.default()
intents.guilds = True
intents.members = True

# The file to store channel configurations
CHANNELS_FILE = 'apod_channels.json'

# --- CACHING & HELPER FUNCTIONS ---

# Simple in-memory cache for the APOD data
apod_cache = {'date': None, 'data': None}
# Keep track of the last posted APOD date to avoid duplicate posts
last_posted_date = None


def load_channels():
    """Loads the channel configuration from the JSON file."""
    if not os.path.exists(CHANNELS_FILE):
        return {}
    try:
        with open(CHANNELS_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


def save_channels(channels):
    """Saves the channel configuration to the JSON file."""
    with open(CHANNELS_FILE, 'w') as f:
        json.dump(channels, f, indent=4)


async def fetch_apod():
    """Fetches APOD from NASA API, using a cache to avoid redundant calls."""
    global apod_cache
    today = date.today().isoformat()

    # If cache is valid for today, return cached data
    if apod_cache['date'] == today and apod_cache['data']:
        return apod_cache['data']

    # Otherwise, fetch from API
    print("Fetching new APOD data from NASA API.")
    api_url = f"https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        apod_data = response.json()

        # Update cache
        apod_cache['date'] = apod_data.get('date')
        apod_cache['data'] = apod_data

        return apod_data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching APOD from NASA API: {e}")
        return None


async def get_resized_image_as_png_file(image_url: str, date_str: str) -> discord.File | None:
    """Downloads an image, resizes it, saves it, and returns a discord.File if it's under 8MB."""
    try:
        response = requests.get(image_url)
        response.raise_for_status()

        # Save the raw image file
        original_filename = os.path.basename(image_url)
        raw_path = os.path.join('cached_raw', original_filename)
        with open(raw_path, 'wb') as f:
            f.write(response.content)
        print(f"Saved raw image to {raw_path}")

        # Open image from bytes
        img = Image.open(io.BytesIO(response.content))

        # Resize the image to have a max width of 1280px
        max_width = 1280
        if img.width > max_width:
            height = int((max_width / img.width) * img.height)
            img = img.resize((max_width, height), Image.Resampling.LANCZOS)
            print(f"Resized image to {max_width}x{height}")

        # Convert to PNG in memory
        with io.BytesIO() as image_binary:
            img.save(image_binary, 'PNG')

            # Check file size before attempting to upload. Discord's limit is 8MB for bots.
            if image_binary.getbuffer().nbytes > 8000000:
                print(f"Resized PNG is still too large ({image_binary.getbuffer().nbytes} bytes).")
                return None

            # Save the converted PNG file
            png_path = os.path.join('cache', f"{date_str}.png")
            with open(png_path, 'wb') as f:
                f.write(image_binary.getvalue())
            print(f"Saved resized PNG image to {png_path}")

            image_binary.seek(0)
            return discord.File(fp=image_binary, filename='apod.png')
    except Exception as e:
        print(f"Failed to process image: {e}")
        return None


# --- BOT INITIALIZATION ---

bot = commands.Bot(command_prefix="!", intents=intents)
apod_channels = load_channels()


# --- BOT EVENTS ---

@bot.event
async def on_ready():
    """Event that runs when the bot is connected and ready."""
    print(f"Logged in as {bot.user}")
    print(f"Bot is on {len(bot.guilds)} servers.")
    check_and_post_apod.start()
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")


# --- COMMANDS ---

async def send_apod_messages(channel: discord.TextChannel, apod_data: dict,
                             interaction: discord.Interaction | None = None):
    """A helper function to send the single combined APOD embed."""
    media_type = apod_data.get('media_type')
    image_url = apod_data.get('hdurl') or apod_data.get('url')
    date_str = apod_data.get('date')
    explanation = apod_data.get('explanation', 'No explanation available.')
    copyright_text = apod_data.get('copyright')

    # 1. Construct the single embed
    embed = discord.Embed(
        title=apod_data.get('title', 'Astronomy Picture of the Day'),
        description=explanation,
        color=discord.Color.from_rgb(54, 57, 63)
    )

    footer_parts = []
    if copyright_text:
        footer_parts.append(f"© {copyright_text.strip()}")
    if date_str:
        footer_parts.append(date_str)
    footer_parts.append("Bot by lunar_sh")

    footer_text = " | ".join(footer_parts)
    embed.set_footer(text=footer_text)

    # 2. Handle image or video
    image_file_to_send = None
    if media_type == 'image' and image_url and date_str:
        image_file_to_send = await get_resized_image_as_png_file(image_url, date_str)
        if image_file_to_send:
            # If we have a file, set the embed to use it.
            embed.set_image(url="attachment://apod.png")
        else:
            # Fallback if image processing fails or file is too large
            embed.add_field(name="Image Link", value=f"[Click here to view image]({image_url})", inline=False)

    elif media_type == 'video' and image_url:
        embed.url = image_url
        embed.title += " (Video)"

    # 3. Send the single message
    if interaction:
        await interaction.followup.send(embed=embed, file=image_file_to_send)
    else:
        await channel.send(embed=embed, file=image_file_to_send)


@bot.tree.command(name="apod", description="Fetches and posts the latest Astronomy Picture of the Day.")
async def apod(interaction: discord.Interaction):
    """Command to manually trigger an APOD post."""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You must be an administrator to use this command.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=False)

    apod_data = await fetch_apod()
    if apod_data:
        await send_apod_messages(interaction.channel, apod_data, interaction)
    else:
        await interaction.followup.send("Sorry, I couldn't fetch the Picture of the Day from NASA right now.")


# Other commands remain the same
@bot.tree.command(name="set_channel", description="Sets this channel for daily APOD posts.")
@app_commands.default_permissions(manage_channels=True)
async def set_channel(interaction: discord.Interaction):
    guild_id = str(interaction.guild.id)
    channel_id = interaction.channel.id
    apod_channels[guild_id] = channel_id
    save_channels(apod_channels)
    await interaction.response.send_message(
        f"This channel (`#{interaction.channel.name}`) is now set for daily APOD posts.", ephemeral=True)


@bot.tree.command(name="unset_channel", description="Stops daily APOD posts in this server.")
@app_commands.default_permissions(manage_channels=True)
async def unset_channel(interaction: discord.Interaction):
    guild_id = str(interaction.guild.id)
    if guild_id in apod_channels:
        del apod_channels[guild_id]
        save_channels(apod_channels)
        await interaction.response.send_message("Daily APOD posts have been disabled for this server.", ephemeral=True)
    else:
        await interaction.response.send_message("No channel is currently set for APOD posts on this server.",
                                                ephemeral=True)


# --- BACKGROUND TASK ---

@tasks.loop(minutes=5)
async def check_and_post_apod():
    """The background task that runs every 5 minutes to check for and post a new APOD."""
    global last_posted_date

    apod_data = await fetch_apod()
    if not apod_data:
        print("Could not fetch APOD data for scheduled check. Skipping.")
        return

    current_apod_date = apod_data.get('date')

    # If the fetched APOD date is different from the last one we posted, post it.
    if current_apod_date != last_posted_date:
        print(f"New APOD found for date: {current_apod_date}. Posting to configured channels.")

        current_channels = load_channels()
        for guild_id, channel_id in current_channels.items():
            try:
                channel = await bot.fetch_channel(channel_id)
                await send_apod_messages(channel, apod_data)
                print(f"Successfully posted APOD to channel {channel_id} in guild {guild_id}")
            except discord.errors.NotFound:
                print(f"Channel {channel_id} not found.")
            except discord.errors.Forbidden:
                print(f"Bot lacks permissions in channel {channel_id}.")
            except Exception as e:
                print(f"An unexpected error occurred when posting to channel {channel_id}: {e}")

        # Update the last posted date to prevent reposting
        last_posted_date = current_apod_date
    else:
        # This can be noisy, so let's not print it every 5 minutes.
        # print(f"APOD for {current_apod_date} has already been posted. Checking again in 5 minutes.")
        pass


# --- RUN THE BOT ---
bot.run(DISCORD_TOKEN)
