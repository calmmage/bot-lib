import asyncio
import logging
import os
import sys
from textwrap import dedent

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from dotenv import load_dotenv

from bot_lib.core import App
from bot_lib.handlers import Handler, BasicHandler, HandlerDisplayMode


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


class FairytaleHandler(Handler):
    name = "fairytale_bot"
    display_mode = HandlerDisplayMode.FULL
    commands = {
        "gpt_complete_handler": ["gpt_complete", "gpt"],
        "fairytale_handler": "fairytale",
    }

    async def gpt_complete_handler(self, message: Message, app: App):
        text = message.text
        response = await app.gpt.complete_text(text)
        # todo: use send_safe util instead
        await message.answer(response)

    fairytale_prompt = dedent(
        """
        Tell a fairytale on a specified topic and fabulate it.
        TOPIC:
        {text}
        """
    )

    # token limit
    FAIRYTALE_TOKEN_LIMIT = 1000

    async def fairytale_handler(self, message: Message, app: App):
        """Tell a fairytale on a sepcified topic and fabulate it."""
        text = message.text
        prompt = self.fairytale_prompt.format(text=text)
        response = await app.gpt.complete_text(
            prompt, max_tokens=self.FAIRYTALE_TOKEN_LIMIT
        )
        # todo: use send_safe util instead
        await message.answer(response)
