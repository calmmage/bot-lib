from aiogram.filters import Command

from bot_lib.core.app import App
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

    for handler in handlers:
        dispatcher.startup.register(handler.on_startup)

        for command, aliases in handler.commands.items():
            dispatcher.message.register(getattr(handler, command), Command(aliases))

        # todo: setup help command somehow - add info to the app?
        #  for the handlers that only have 'help' visibility


def setup_bot(bot, bot_config: BotConfig, extra_handlers=None):

    # todo: set bot commands

    # async def _set_aiogram_bot_commands(self):
    #     bot_commands = [
    #         types.BotCommand(command=c, description=d or self.NO_COMMAND_DESCRIPTION)
    #         for c, d in self.commands
    #     ]
    #     await self._aiogram_bot.set_my_commands(bot_commands)
    pass
