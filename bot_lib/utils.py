import asyncio
import logging
import os
import sys

from aiogram import Bot
from aiogram import Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv

from bot_lib import (
    BotConfig,
    setup_dispatcher,
)


def create_bot(token=None):
    if token is None:
        load_dotenv()
        # Bot token can be obtained via https://t.me/BotFather
        token = os.getenv("TELEGRAM_BOT_TOKEN")
    bot = Bot(
        token,  # parse_mode=ParseMode.HTML
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    return bot


def setup_bot(app, handlers=None):
    bot_config = BotConfig(app=app)

    # set up dispatcher
    dp = Dispatcher()
    setup_dispatcher(dp, bot_config, extra_handlers=handlers)
    bot = create_bot()
    return dp, bot


def run_bot(dp, bot):
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(dp.start_polling(bot))
