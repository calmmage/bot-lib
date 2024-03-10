from aiogram import Dispatcher
from aiogram.types import Message
from dotenv import load_dotenv

from bot_lib import App, Handler, HandlerDisplayMode, BotConfig, setup_dispatcher
from bot_lib.demo import create_bot, run_bot


class MyApp(App):
    secret_message = "Hello, Calm world!"


class MyHandler(Handler):
    name = "myBot"
    display_mode = HandlerDisplayMode.FULL

    async def custom_handler(self, message: Message, app: MyApp):
        await message.answer(app.secret_message)


bot_config = BotConfig(app=MyApp())

# set up dispatcher
dp = Dispatcher()

setup_dispatcher(dp, bot_config, extra_handlers=[MyHandler()])

load_dotenv()
bot = create_bot()

if __name__ == "__main__":
    run_bot(dp, bot)
