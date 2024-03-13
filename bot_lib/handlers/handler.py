import enum
from typing import List, Dict

from aiogram import Bot
from aiogram.types import Message
from deprecated import deprecated

from bot_lib.migration_bot_base.core.telegram_bot import TelegramBot as OldTelegramBot
from bot_lib.core.app import App


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
    commands: Dict[str, List[str]] = {}  # dict handler_func_name -> command aliases
    plugins_required: List[str] = None

    # todo: build this automatically from app?
    get_commands = []  # list of tuples (app_func_name, handler_func_name)
    set_commands = []  # list of tuples (app_func_name, handler_func_name)

    def __init__(self):
        self.bot = None
        self._build_commands_and_add_to_list()

    # todo: check if I can pass the bot on startup - automatically by dispatcher?
    def on_startup(self, bot: Bot):
        self.bot = bot

    async def send_safe(self, message: str, chat_id: int):
        # await self.bot.send_message(chat_id, message)
        raise NotImplementedError("Method send_safe is not implemented")

    @property
    @deprecated(
        version="1.0.0",
        reason="Found old (pre-migration) style usage of _aiogram_bot. please rework and replace with self.bot",
    )
    def _aiogram_bot(self):
        return self.bot

    @staticmethod
    def get_user(message, forward_priority=False):
        if forward_priority and hasattr(message, "forward_from"):
            user = message.forward_from
        else:
            user = message.from_user
        return user.username or user.id

    def _build_commands_and_add_to_list(self):
        for app_func_name, handler_func_name in self.get_commands:
            handler = self._build_simple_get_handler(app_func_name)
            setattr(self, handler_func_name, handler)
            self.commands[handler_func_name] = app_func_name
        for app_func_name, handler_func_name in self.set_commands:
            handler = self._build_simple_set_handler(app_func_name)
            setattr(self, handler_func_name, handler)
            self.commands[handler_func_name] = app_func_name

    def _build_simple_set_handler(self, name: str):
        async def handler(message: Message, app: App):
            text = self.strip_command(message.text)
            user = self.get_user(message)
            func = getattr(app, name)
            result = func(text, user)
            await message.answer(result)

        return handler

    def _build_simple_get_handler(self, name: str):
        async def handler(message: Message, app: App):
            user = self.get_user(message)
            func = getattr(app, name)
            result = func(user)
            await message.answer(result)

        return handler

    async def _send_as_file(
        self, chat_id, text, reply_to_message_id=None, filename=None
    ):
        """
        Send text as a file to the chat
        :param chat_id:
        :param text:
        :param reply_to_message_id:
        :param filename:
        :return:
        """
        from aiogram.types.input_file import BufferedInputFile

        temp_file = BufferedInputFile(text.encode("utf-8"), filename)
        await self.bot.send_document(
            chat_id, temp_file, reply_to_message_id=reply_to_message_id
        )

    @staticmethod
    def strip_command(text: str):
        if text.startswith("/"):
            parts = text.split(" ", 1)
            if len(parts) > 1:
                return parts[1].strip()
            return ""
