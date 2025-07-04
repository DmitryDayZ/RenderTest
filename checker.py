import os
import asyncio
import logging
from aiogram import Bot
from dotenv import load_dotenv
from pybit.unified_trading import HTTP

# Загружаем .env
load_dotenv()

# Переменные из окружения
BOT_TOKEN = os.getenv("BOT_TOKEN", "6363721955:AAEyulmzYj5hF45DPJV1TWLCw_hRj6Y_jx0")
CHAT_ID = int(os.getenv("CHAT_ID",-4907450617))
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", 5))
THRESHOLD_PERCENT = float(os.getenv("THRESHOLD_PERCENT", 0.1))
BYBIT_TESTNET = os.getenv("BYBIT_TESTNET", "false").lower() == "true"

# Бот и pybit-сессия
bot = Bot(token=BOT_TOKEN)
session = HTTP(testnet=BYBIT_TESTNET)

last_value = None

def fetch_price() -> float:
    """Получает последнюю цену BTCUSDT"""
    data = session.get_tickers(category="linear", symbol="ETHUSDT")
    return float(data["result"]["list"][0]["lastPrice"])




async def check_loop():
    """Цикл, проверяющий изменение цены"""
    global last_value
    while True:
        try:
            current = await asyncio.to_thread(fetch_price)
            if last_value is not None:
                diff = abs(current - last_value) / last_value * 100
                if diff >= THRESHOLD_PERCENT:
                    msg = f"📊 Зміна: {diff:.2f}%\nБуло: {last_value}\nСтало: {current}"
                else:
                    msg = f"ℹ️ Ціна не змінилась суттєво: {current}"
                    await bot.send_message(CHAT_ID, msg)
            last_value = current
        except Exception as e:
            logging.warning(f"⚠️ Помилка отримання ціни: {e}")
        await asyncio.sleep(POLL_INTERVAL)
