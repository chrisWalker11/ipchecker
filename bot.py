import os
import discord
import aiohttp
import logging
from discord.ext import tasks

# ——— Configuration ———
TOKEN = '<TOKEN>'
CHANNEL_ID          = <channel_id>
CHECK_INTERVAL_HOURS = 6

BASE_DIR = os.path.dirname(__file__)
IP_FILE  = os.path.join(BASE_DIR, 'ip_cache.txt')

# ——— Logging ———
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# ——— Discord Setup ———
intents = discord.Intents.default()
client  = discord.Client(intents=intents)
last_ip = None  # will be loaded on ready

def load_last_ip():
    try:
        with open(IP_FILE, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def save_current_ip(ip):
    with open(IP_FILE, 'w') as f:
        f.write(ip)

async def fetch_public_ip():
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get('https://api.ipify.org') as resp:
            resp.raise_for_status()
            return await resp.text()

@tasks.loop(hours=CHECK_INTERVAL_HOURS)
async def ip_checker():
    global last_ip
    try:
        new_ip = await fetch_public_ip()

        # Seed on first run: write and return without pinging
        if last_ip is None:
            save_current_ip(new_ip)
            last_ip = new_ip
            log.info(f"Seeded initial IP: {new_ip}")
            return

        # Only ping if it’s changed
        if new_ip != last_ip:
            channel = client.get_channel(CHANNEL_ID)
            if not channel:
                log.error(f"Channel {CHANNEL_ID} not found or bot lacks access.")
                return

            msg = (
                f"@everyone 🔄 IP changed:\n"
                f"Old: `{last_ip}`\n"
                f"New: `{new_ip}`"
            )
            await channel.send(msg)

            save_current_ip(new_ip)
            last_ip = new_ip

    except Exception:
        log.exception("Error during IP check")

@client.event
async def on_ready():
    global last_ip
    log.info(f"Logged in as {client.user} (ID: {client.user.id})")
    last_ip = load_last_ip()
    if not ip_checker.is_running():
        ip_checker.start()

if __name__ == '__main__':
    client.run(TOKEN)
