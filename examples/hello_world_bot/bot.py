from aiogram import Dispatcher
from dotenv import load_dotenv

from bot_lib.demo import create_bot, configure_commands_and_dispatcher, run_bot

load_dotenv()


def setup_and_run_bot():
    dp = Dispatcher()
    # step 1 - configure commands and dispatcher
    configure_commands_and_dispatcher(dp)

    # step 2 - setup bot
    bot = create_bot()

    # step 3 - run bot
    run_bot(dp, bot)


# def setup_bot(bot, handlers):
# setup bot to bind to handlers


if __name__ == '__main__':
    setup_and_run_bot()
