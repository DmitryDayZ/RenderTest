import os
import asyncio
import logging
from aiohttp import ClientSession
from aiogram import Bot
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
API_URL = os.getenv("API_URL")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", 60))
THRESHOLD_PERCENT = float(os.getenv("THRESHOLD_PERCENT", 2))

bot = Bot(token=BOT_TOKEN)
last_value = None

async def fetch_value(session: ClientSession) -> float:
    async with session.get(API_URL) as resp:
        data = await resp.json()
        return float(data["value"])  # ⚠️ адаптуй під API

async def check_loop():
    global last_value
    async with ClientSession() as session:
        while True:
            try:
                current = await fetch_value(session)
                if last_value is not None:
                    diff = abs(current - last_value) / last_value * 100
                    if diff >= THRESHOLD_PERCENT:
                        msg = f"📊 Зміна: {diff:.2f}%\nБуло: {last_value}\nСтало: {current}"
                        await bot.send_message(CHAT_ID, msg)
                last_value = current
            except Exception as e:
                logging.warning(f"⚠️ Помилка API: {e}")
            await asyncio.sleep(POLL_INTERVAL)
