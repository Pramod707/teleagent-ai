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
# System prompt
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


# --------------------------------------------------
# Store conversation history per Telegram user
# --------------------------------------------------

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
# /clear
# --------------------------------------------------


@dp.message(Command("clear"))
async def clear_handler(message: types.Message):

    user_id = message.from_user.id

    # Clear only this user's conversation
    user_histories[user_id] = [SYSTEM_MESSAGE.copy()]

    await message.answer("Conversation history cleared 🧹")


# --------------------------------------------------
# /help
# --------------------------------------------------


@dp.message(Command("help"))
async def help_handler(message: types.Message):

    help_command = """
<b>Here’s a quick rundown of what I can help you with:</b>

<b>🛠️ Common tasks</b>

• <b>Code snippets</b> — Python, JavaScript, and other programming languages.

• <b>Debugging help</b> — Share an error or code, and I’ll help you find the problem.

• <b>Explanation of concepts</b> — Programming, mathematics, science, history, and more.

• <b>Writing assistance</b> — Emails, essays, summaries, documentation, and creative writing.

• <b>Data manipulation</b> — Pandas, NumPy, SQL queries, and data-processing tasks.

• <b>General questions</b> — Facts, definitions, how-to questions, and recommendations.

<b>💡 How to get the most out of me</b>

1. <b>Be specific</b> — The more detail you provide, the better I can help.

2. <b>Provide context</b> — Share your existing code, project details, or environment when relevant.

3. <b>Ask follow-up questions</b> — We can continue the conversation and refine the solution.

Just type your request and I’ll jump right in!
"""

    await message.answer(help_command, parse_mode="HTML")


# --------------------------------------------------
# Normal messages
# --------------------------------------------------


@dp.message()
async def groq_handler(message: types.Message):

    # Ignore empty messages
    if not message.text:
        return

    print(f">>> User:\n\t{message.text}")

    # Get Telegram user's unique ID
    user_id = message.from_user.id

    # Get this user's conversation history
    messages = get_user_history(user_id)

    # Add user's message
    messages.append({"role": "user", "content": message.text})

    # Send conversation history to Groq
    response = client.chat.completions.create(model=model_name, messages=messages)

    # Get assistant response
    assistant_response = response.choices[0].message.content

    # Save assistant response to this user's history
    messages.append({"role": "assistant", "content": assistant_response})

    print(f"<<< Groq:\n\t{assistant_response}")

    # Send response back to Telegram
    await message.answer(assistant_response)


# --------------------------------------------------
# Main
# --------------------------------------------------


async def main():

    print("Bot is starting...")

    await dp.start_polling(bot)


# --------------------------------------------------
# Run application
# --------------------------------------------------

if __name__ == "__main__":
    asyncio.run(main())
