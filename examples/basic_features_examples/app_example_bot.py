from typing import List

from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv

from bot_lib import App, Handler, HandlerDisplayMode
from bot_lib.demo import create_bot, run_bot


class MyApp(App):
    secret_message = "Hello, Calm world!"


class MyHandler(Handler):
    name = "myBot"
    display_mode = HandlerDisplayMode.FULL

    async def custom_handler(self, message: Message, app: MyApp):
        await message.answer(app.secret_message)


def bind_bot_to_handler_on_dispatcher_startup(handler: Handler, dispatcher: Dispatcher):
    dispatcher.startup.register(handler.on_startup)


def bind_bot_to_handlers_on_dispatcher_startup(
    handlers: List[Handler], dispatcher: Dispatcher
):
    # todo: check if this doesn't override the previous handlers
    for handler in handlers:
        dispatcher.startup.register(handler.on_startup)


# set up dispatcher
dp = Dispatcher()
dp["app"] = MyApp()

handler = MyHandler()
# todo: move to core utils / decorators / auto-machinery
dp.message.register(handler.custom_handler, Command("custom"))

# todo: move to core utils
dp.startup.register(handler.on_startup)

load_dotenv()
bot = create_bot()

if __name__ == "__main__":
    run_bot(dp, bot)
