import asyncio
from pathlib import Path
import os

from groq import Groq
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command


# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")

print("Token loaded:", telegram_token is not None)
print("Groq key loaded:", GROQ_API_KEY is not None)


# --------------------------------------------------
# Initialize Groq
# --------------------------------------------------

client = Groq(api_key=GROQ_API_KEY)

model_name = "groq/compound-mini"


# --------------------------------------------------
# Initialize Telegram bot
# --------------------------------------------------

bot = Bot(token=telegram_token)
dp = Dispatcher()


# --------------------------------------------------
# Store conversation reference
# --------------------------------------------------


class Reference:
    """Store the conversation history."""

    def __init__(self) -> None:
        self.messages = [{"role": "system", "content": "You are a helpful assistant"}]


reference = Reference()


# --------------------------------------------------
# /start
# --------------------------------------------------


@dp.message(CommandStart())
async def start_handler(message: types.Message):
    """Handler for the /start command."""

    await message.answer("Hello! I am TeleAgent 🤖. How can I assist you?")


# --------------------------------------------------
# Normal messages
# --------------------------------------------------


@dp.message()
async def groq_handler(message: types.Message):

    print(f">>> User:\n\t{message.text}")

    # Add user's message to history
    reference.messages.append({"role": "user", "content": message.text})

    response = client.chat.completions.create(
        model="groq/compound-mini", messages=reference.messages
    )

    assistant_response = response.choices[0].message.content

    # Add Groq's response to history
    reference.messages.append({"role": "assistant", "content": assistant_response})

    print(f"<<< Groq:\n\t{assistant_response}")

    await message.answer(assistant_response)


# --------------------------------------------------
# /clear
# --------------------------------------------------
def clear_past():
    """Clear the conversation history."""

    reference.messages = [{"role": "system", "content": "You are a helpful assistant"}]


# --------------------------------------------------
# /help
# --------------------------------------------------


@dp.message(Command("help"))
async def help_handler(message: types.Message):
    """Display the help menu."""

    help_command = """
Hi There, I'm Groq-AI Telegram Bot 🤖!

Please follow these commands:

/start - Start the bot
/clear - Clear the past conversation and context
/help - Display this help menu
"""

    await message.answer(help_command)


# --------------------------------------------------
# Main
# --------------------------------------------------


async def main():

    print("Bot is starting...")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
