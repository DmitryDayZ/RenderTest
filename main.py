import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from checker import check_loop, BOT_TOKEN

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Привет! Я бот, который отслеживает цену ETHUSDT и сообщает об изменениях.")

@dp.message()
async def get_chat_id(message: types.Message):
    chat_id = message.chat.id
    await message.answer(f"ID этого чата: {chat_id}")
#
# @dp.message()
# async def echo(msg: types.Message):
#     await msg.answer("✅ Бот працює!")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    asyncio.create_task(check_loop())
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
