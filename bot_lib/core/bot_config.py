from aiogram import types
from aiogram.filters import Command

# todo: use calmlib logger
from loguru import logger
from bot_lib.core.app import App
from bot_lib.handlers.handler import HandlerDisplayMode
from bot_lib.handlers.basic_handler import BasicHandler


class BotConfig:
    DEFAULT_APP = App
    DEFAULT_HANDLERS = [
        BasicHandler,
    ]

    def __init__(self, app: App = None, handlers: tuple = None):
        if app is None:
            app = self.DEFAULT_APP()
        self.app = app
        if handlers is None:
            handlers = self.DEFAULT_HANDLERS
        self.handlers = handlers


def setup_dispatcher(dispatcher, bot_config: BotConfig, extra_handlers=None):
    dispatcher["app"] = bot_config.app

    handlers = [handler() for handler in bot_config.handlers]
    if extra_handlers:
        handlers += extra_handlers

    # step 1 - build commands list
    commands = []

    for handler in handlers:
        dispatcher.startup.register(handler.on_startup)

        # todo: add other display modes processing
        for command, aliases in handler.commands.items():
            # register commands
            dispatcher.message.register(
                getattr(handler, command), Command(commands=aliases)
            )

            # todo: use calmlib util - 'compare enums' - find wind find_ and add to calmlib
            if handler.display_mode == HandlerDisplayMode.FULL:
                # commands descriptions
                if isinstance(aliases, str):
                    aliases = [aliases]
                for alias in aliases:
                    commands.append((alias, getattr(handler, command).__doc__))
            elif handler.display_mode == HandlerDisplayMode.HELP_COMMAND:
                # todo: setup help command somehow - add info to the app?
                #  for the handlers that only have 'help' visibility
                pass

    # here's an example:
    NO_COMMAND_DESCRIPTION = "No description"

    # todo: make this less ugly
    async def _set_aiogram_bot_commands(bot):
        # assert all commands are lowercase and unique
        bot_commands = []
        for c, d in commands:
            if not c.islower():
                raise ValueError(f"Command is not lowercase: {c}")
            if c in [bc.command for bc in bot_commands]:
                logger.warning(f"Duplicate command: {c}")
                continue
            bot_commands.append(
                types.BotCommand(command=c, description=d or NO_COMMAND_DESCRIPTION)
            )
        logger.debug(f"Setting bot commands: {bot_commands}")
        await bot.set_my_commands(bot_commands)

    dispatcher.startup.register(_set_aiogram_bot_commands)


def setup_bot(bot, bot_config: BotConfig, extra_handlers=None):

    # todo: set bot commands

    # async def _set_aiogram_bot_commands(self):
    #     bot_commands = [
    #         types.BotCommand(command=c, description=d or self.NO_COMMAND_DESCRIPTION)
    #         for c, d in self.commands
    #     ]
    #     await self._aiogram_bot.set_my_commands(bot_commands)
    pass
