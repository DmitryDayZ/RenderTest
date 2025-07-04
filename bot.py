import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from checker import check_loop, BOT_TOKEN

dp = Dispatcher()

@dp.message()
async def echo(msg: types.Message):
    await msg.answer("✅ Бот працює!")

async def main():
    bot = Bot(token=BOT_TOKEN)
    await bot.delete_webhook(drop_pending_updates=True)
    dp.include_router(dp)
    asyncio.create_task(check_loop())
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
