import pytest
from aiogram import Dispatcher
from aiogram.types import Message
from calmapp import App

from bot_lib import Handler, HandlerDisplayMode, BotConfig, setup_dispatcher


class MyApp(App):
    secret_message = "Hello, Calm world!"


class MyHandler(Handler):
    name = "myBot"
    display_mode = HandlerDisplayMode.FULL

    async def custom_handler(self, message: Message, app: MyApp):
        await message.answer(app.secret_message)


class TestSetup:
    def test_setup(self):

        app = MyApp()
        bot_config = BotConfig(app=app)

        # set up dispatcher
        dp = Dispatcher()

        my_handler = MyHandler()
        handlers = [my_handler]
        setup_dispatcher(dp, bot_config, extra_handlers=handlers)
