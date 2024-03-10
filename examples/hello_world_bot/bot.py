import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from dotenv import load_dotenv

from bot_lib import setup_bot


def setup_and_run_bot():
    # step 1 - configure commands and dispatcher
    dispatcher = configure_commands_and_dispatcher()

    # step 2 - setup bot
    bot = setup_bot()

    # step 3 - run bot
    run_bot(dispatcher, bot)


def configure_commands_and_dispatcher():
    # All handlers should be attached to the Router (or Dispatcher)
    dp = Dispatcher()

    @dp.message(CommandStart())
    async def command_start_handler(message: Message) -> None:
        await message.answer(f"Hello, {hbold(message.from_user.full_name)}!")

    @dp.message()
    async def echo_handler(message: types.Message) -> None:
        try:
            await message.send_copy(chat_id=message.chat.id)
        except TypeError:
            await message.answer("Nice try!")

    return dp


def setup_bot():
    load_dotenv()

    # Bot token can be obtained via https://t.me/BotFather
    TOKEN = getenv("TELEGRAM_BOT_TOKEN")
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    return bot


def run_bot(dp, bot):
    if __name__ == "__main__":
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        asyncio.run(dp.start_polling(bot))


setup_and_run_bot()
