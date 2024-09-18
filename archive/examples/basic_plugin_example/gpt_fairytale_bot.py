from aiogram import Dispatcher
from dotenv import load_dotenv

from bot_lib import (
    BotManager,
    setup_dispatcher,
    App,
)
from bot_lib.demo import FairytaleHandler
from bot_lib.utils import create_bot, run_bot
from bot_lib.plugins import GptPlugin

load_dotenv()
plugins = [GptPlugin]
app = App(plugins=plugins)
bot_config = BotManager(app=app)

# set up dispatcher
dp = Dispatcher()

fairytale_handler = FairytaleHandler()
handlers = [fairytale_handler]
setup_dispatcher(dp, bot_config, extra_handlers=handlers)

bot = create_bot()

if __name__ == "__main__":
    run_bot(dp, bot)
