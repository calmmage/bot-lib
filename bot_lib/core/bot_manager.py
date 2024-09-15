from typing import Callable, Awaitable, Dict, Any

from aiogram import F
from aiogram import types, Bot
from aiogram.enums.chat_type import ChatType
from aiogram.filters import Command
from aiogram.types import Update
from loguru import logger
from typing_extensions import deprecated

from bot_lib.handlers.basic_handler import BasicHandler
from bot_lib.handlers.handlerbase import HandlerDisplayMode
from calmapp import App


class BotManager:
    # todo: rewrite this to be Pydantic basesettings and load from env
    DEFAULT_APP = App
    DEFAULT_HANDLERS = [
        BasicHandler,
    ]

    def __init__(self, app: App = None, handlers: tuple = None):
        if app is None:
            app = self.DEFAULT_APP()
        self.app: App = app
        if handlers is None:
            handlers = self.DEFAULT_HANDLERS
        self.handlers = handlers

    def setup_dispatcher(self, dispatcher, extra_handlers=None):
        dispatcher["app"] = self.app

        # todo: use "instantiate_classes" method that I wrote somewhere..
        # todo: pass plugins? or just assign to dispatcher? nah, i can use via App
        handlers = [handler() for handler in self.handlers]
        if extra_handlers:
            handlers += extra_handlers

        commands = self._register_handlers(dispatcher, handlers)
        self._setup_set_bot_commands(dispatcher, commands)
        self._setup_print_bot_url(dispatcher)

        if self.app.config.plugin_flags.enable_message_history:
            dispatcher.update.outer_middleware.register(self.message_history_middleware)

    async def message_history_middleware(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        await self.app.message_history.save_update(event.model_dump(exclude_none=True))
        return await handler(event, data)

    # todo: split this even more
    def _register_handlers(self, dispatcher, handlers):
        # step 1 - build commands list
        commands = []
        for handler in handlers:
            dispatcher.startup.register(handler.on_startup)

            router = handler.get_router()
            handler.setup_router(router)

            # todo: add other display modes processing
            for command, aliases in handler.commands.items():
                # register commands
                if isinstance(aliases, str):
                    aliases = [aliases]
                aliases = [alias.lstrip("/") for alias in aliases]
                router.message.register(getattr(handler, command), Command(commands=aliases))

                # todo: use calmlib util - 'compare enums' - find wind find_ and add to calmlib
                if handler.display_mode == HandlerDisplayMode.FULL:
                    # commands descriptions
                    for alias in aliases:
                        commands.append((alias, getattr(handler, command).__doc__))
                elif handler.display_mode == HandlerDisplayMode.HELP_MESSAGE:
                    # todo: rework this to store the whole handler class
                    #  then if general 'help' is called - list available handlers
                    #  if /help <handler> is called - list commands for that handler
                    self.app.hidden_commands[handler.name].extend(aliases)

            if handler.display_mode == HandlerDisplayMode.HELP_COMMAND:
                name = handler.name or handler.__class__.__name__
                alias = f"help_{name.lower()}"
                router.message.register(handler.nested_help_handler, Command(commands=[alias]))
                commands.append((alias, "Show help for {name} - list all available commands"))

            handler.register_extra_handlers(router)

            if handler.has_chat_handler:
                # todo: only react on messages with text / content - ignore pins etc.
                # todo: add flexible config to support both group and private chats
                router.message.register(handler.chat_handler, F.chat.type == ChatType.PRIVATE)

            if handler.has_error_handler:
                dispatcher.error.register(handler.error_handler, F.update.message.as_("message"))

            dispatcher.include_router(router)

        return commands

    def _setup_set_bot_commands(self, dispatcher, commands):
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
                bot_commands.append(types.BotCommand(command=c, description=d or NO_COMMAND_DESCRIPTION))
            logger.debug(f"Setting bot commands: {bot_commands}")
            await bot.set_my_commands(bot_commands)

        dispatcher.startup.register(_set_aiogram_bot_commands)

    def _setup_print_bot_url(self, dispatcher):
        async def print_bot_url(bot: Bot):
            bot_info = await bot.get_me()
            # logger.info(f"Bot info: {bot_info}")
            logger.info(f"Bot url: https://t.me/{bot_info.username}")

        dispatcher.startup.register(print_bot_url)


@deprecated("Use BotConfig.setup_dispatcher instead")
def setup_dispatcher(dispatcher, bot_config: BotManager, extra_handlers=None):
    bot_config.setup_dispatcher(dispatcher, extra_handlers)


BotConfig = BotManager
