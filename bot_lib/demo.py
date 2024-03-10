import asyncio
import logging
import os
import sys

from aiogram import types, Bot
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from dotenv import load_dotenv

from bot_lib.handlers import BasicHandler


# load_dotenv()

def create_bot(token=None):
    if token is None:
        load_dotenv()
        # Bot token can be obtained via https://t.me/BotFather
        token = os.getenv("TELEGRAM_BOT_TOKEN")
    bot = Bot(token, parse_mode=ParseMode.HTML)
    return bot


def configure_commands_and_dispatcher(dp):
    # All handlers should be attached to the Router (or Dispatcher)

    @dp.message(CommandStart())
    async def command_start_handler(message: Message) -> None:
        await message.answer(f"Hello, {hbold(message.from_user.full_name)}!")

    return dp


def run_bot(dp, bot):
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(dp.start_polling(bot))


def setup_dispatcher_with_demo_handler(dp):
    """
    Idea: register a help command from the handler - manually
    :param dp:
    :return:
    """

    handler = BasicHandler()

    dp.message.register(handler.help_handler, Command("help"))
