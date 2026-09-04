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

BASE_DIR = Path(__file__).resolve().parent.parent
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
# Store conversation history per Telegram user
# --------------------------------------------------

SYSTEM_MESSAGE = {
    "role": "system",
    "content": """
You are TeleAgent, a helpful and conversational AI assistant inside Telegram.

Respond naturally and concisely.

Use plain text formatting suitable for Telegram.

Do not generate Markdown links.
Do not generate URLs unless the user explicitly asks for a link.
Do not include unnecessary emojis.
Do not provide a generic list of capabilities unless the user asks what you can do.

Answer the user's actual question directly.
""",
}

user_histories = {}


def get_user_history(user_id: int):
    """Get or create conversation history for a Telegram user."""

    if user_id not in user_histories:
        user_histories[user_id] = [SYSTEM_MESSAGE.copy()]

    return user_histories[user_id]


# --------------------------------------------------
# /start
# --------------------------------------------------


@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer("Hello! I am TeleAgent 🤖. How can I assist you?")


# --------------------------------------------------
# Normal messages
# --------------------------------------------------


@dp.message()
async def groq_handler(message: types.Message):

    print(f">>> User:\n\t{message.text}")

    user_id = message.from_user.id

    messages = get_user_history(user_id)

    messages.append({"role": "user", "content": message.text})

    response = client.chat.completions.create(model=model_name, messages=messages)

    assistant_response = response.choices[0].message.content

    messages.append({"role": "assistant", "content": assistant_response})

    print(f"<<< Groq:\n\t{assistant_response}")

    await message.answer(assistant_response)


# --------------------------------------------------
# /clear
# --------------------------------------------------


@dp.message(Command("clear"))
async def clear_handler(message: types.Message):

    user_id = message.from_user.id

    user_histories[user_id] = [SYSTEM_MESSAGE.copy()]

    await message.answer("Conversation history cleared 🧹")


# --------------------------------------------------
# /help
# --------------------------------------------------


@dp.message(Command("help"))
async def help_handler(message: types.Message):

    help_command = """
Hi! I'm TeleAgent 🤖

Available commands:

/start - Start the bot
/clear - Clear your conversation history
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
