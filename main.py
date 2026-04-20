from aiogram import Router, F, Bot, Dispatcher
from dotenv import load_dotenv
import asyncio
import logging
import os
from handlers.handler import router


if not os.path.exists("photos"):
    os.makedirs("photos")


load_dotenv()
BOT_TOKEN = os.getenv("TOKEN")



logging.basicConfig(level=logging.INFO)

print("All hail Lelouch!")
async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(bot)




if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("All hail Lelouch!")