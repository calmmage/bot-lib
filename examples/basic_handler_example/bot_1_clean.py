"""
Only use bot-lib to create a bot
"""

from aiogram import Dispatcher
from dotenv import load_dotenv

from bot_lib.demo import create_bot, run_bot, setup_dispatcher_with_demo_handler

# from bot_lib import create_bot
load_dotenv()

def setup_and_run_bot():
    dp = Dispatcher()
    # step 1 - configure commands and dispatcher
    # configure_commands_and_dispatcher(dp)
    setup_dispatcher_with_demo_handler(dp)

    # step 2 - setup bot
    bot = create_bot()

    # step 3 - run bot
    run_bot(dp, bot)



if __name__ == '__main__':
    setup_and_run_bot()
