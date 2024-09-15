from aiogram import Dispatcher
from aiogram.types import Message
from dotenv import load_dotenv

from bot_lib import (
    HandlerBase,
    HandlerDisplayMode,
    BotManager,
    setup_dispatcher,
)
from bot_lib.utils import create_bot, run_bot
from calmapp import App, Plugin


class MyPlugin(Plugin):
    name = "my_plugin"

    secret_message = "Hello, Plugin world!"


class MyApp(App):
    @property
    def my_plugin(self) -> MyPlugin:
        if "my_plugin" not in self.plugins:
            raise AttributeError("MyPlugin is not enabled.")
        return self.plugins["my_plugin"]


class MyHandler(HandlerBase):
    name = "myBot"
    display_mode = HandlerDisplayMode.FULL
    commands = {"custom_handler": "custom"}

    async def custom_handler(self, message: Message, app: MyApp):
        await message.answer(app.my_plugin.secret_message)


bot_config = BotManager(app=MyApp(plugins=[MyPlugin]))

# set up dispatcher
dp = Dispatcher()

setup_dispatcher(dp, bot_config, extra_handlers=[MyHandler()])

load_dotenv()
bot = create_bot()

if __name__ == "__main__":
    run_bot(dp, bot)
