import os
import asyncio
import logging
from aiogram import Bot
from dotenv import load_dotenv
from binance.um_futures import UMFutures  # Клиент Binance Futures

# 🔧 Настройка логирования — будет выводить время, уровень и сообщение
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# Загружаем переменные окружения из .env файла
load_dotenv()

# Конфигурационные переменные
BOT_TOKEN = os.getenv("BOT_TOKEN") or "6363721955:AAEyulmzYj5hF45DPJV1TWLCw_hRj6Y_jx0"  # Токен Telegram-бота
CHAT_ID = os.getenv("CHAT_ID") or "-4907450617"  # ID чата для уведомлений
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL") or 30)  # Интервал опроса в секундах
THRESHOLD_PERCENT = float(os.getenv("THRESHOLD_PERCENT") or 2)  # Пороговое изменение (%)
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "")  # API ключ от Binance (необязателен для публичных запросов)
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET", "")  # API секрет

# Инициализация Telegram-бота
bot = Bot(token=BOT_TOKEN)

# Инициализация клиента Binance Futures (можно без ключей)
client = UMFutures(key=BINANCE_API_KEY, secret=BINANCE_API_SECRET)

# Переменная для хранения последней известной цены
last_price = None

def fetch_price() -> float:
    """
    Получение текущей цены ETHUSDT с Binance Futures.
    Эта функция синхронная — используется внутри asyncio.to_thread.
    """
    data = client.ticker_price(symbol="ETHUSDT")
    price = float(data["price"])
    logging.debug(f"🔄 Получена цена с Binance: {price}")
    return price

async def check_loop():
    """
    Циклически проверяет цену ETHUSDT и отправляет уведомление при изменении на заданный процент.
    """
    global last_price
    logging.info("🚀 Старт мониторинга цены ETHUSDT")

    while True:
        try:
            # Получаем текущую цену в отдельном потоке, т.к. py-binance не асинхронный
            current = await asyncio.to_thread(fetch_price)
            logging.info(f"📈 Текущая цена: {current}")

            # Если уже есть предыдущая цена — вычисляем разницу
            if last_price is not None:
                diff = abs(current - last_price) / last_price * 100
                logging.info(f"📊 Изменение: {diff:.4f}%")

                # Если изменение превышает порог — шлём уведомление
                if diff >= THRESHOLD_PERCENT:
                    msg = f"📊 Изменение цены ETHUSDT: {diff:.2f}%\nБыло: {last_price}\nСтало: {current}"
                    await bot.send_message(CHAT_ID, msg)
                    logging.info("📩 Отправлено уведомление о значительном изменении")
                else:
                    # При незначительном изменении — также уведомляем (опционально)
                    msg = f"ℹ️ Цена ETHUSDT существенно не изменилась: {diff:.2f}%\nТекущая цена: {current}"
                    await bot.send_message(CHAT_ID, msg)
                    logging.debug("✅ Изменение не превышает порог, отправлено уведомление")
            else:
                logging.info("🔔 Начальная установка цены")

            last_price = current  # Обновляем цену

        except Exception as e:
            logging.warning(f"⚠️ Ошибка при получении цены: {e}")

        # ⏲ Ждём заданный интервал перед следующей проверкой
        await asyncio.sleep(POLL_INTERVAL)
