import enum
from typing import List, Dict

from aiogram import Bot
from deprecated import deprecated

from bot_lib.migration_bot_base.core.telegram_bot import TelegramBot as OldTelegramBot


class HandlerDisplayMode(enum.Enum):
    FULL = "full"  # each command is displayed separately
    HELP_MESSAGE = "help_message"
    # help message is displayed in the main help command
    # e.g. /help dev

    HELP_COMMAND = "help_command"  # separate help command e.g. /help_dev
    HIDDEN = "hidden"  # hidden from help command


# abstract
class Handler(OldTelegramBot):  # todo: add abc.ABC back after removing OldTelegramBot
    name: str = None
    display_mode: HandlerDisplayMode = HandlerDisplayMode.HELP_COMMAND
    commands: Dict[str, List[str]] = None
    plugins_required: List[str] = None

    def __init__(self):
        self.bot = None

    # todo: check if I can pass the bot on startup - automatically by dispatcher?
    def on_startup(self, bot: Bot):
        self.bot = bot

    async def send_safe(self, message: str, chat_id: int):
        # await self.bot.send_message(chat_id, message)
        raise NotImplementedError("Method send_safe is not implemented")

    @property
    @deprecated(version="1.0.0", reason="Found old (pre-migration) style usage of _aiogram_bot. please rework and replace with self.bot")
    def _aiogram_bot(self):
        return self.bot
