import asyncio
from pathlib import Path
import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")

print("Token loaded:", telegram_token is not None)

bot = Bot(token=telegram_token)
dp = Dispatcher()


@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer("Hello! I am TeleAgent 🤖")


async def main():
    print("Bot is starting...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
