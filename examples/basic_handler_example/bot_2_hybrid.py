"""
Use both bot-lib and raw aiogram methods to create a bot
use demo utils to focus on bot-lib and hide the aiogram methods a little bit

"""
from aiogram import Dispatcher, types
# from aiogram.filters import Command
from dotenv import load_dotenv

from bot_lib.demo import create_bot, configure_commands_and_dispatcher, run_bot, \
    setup_dispatcher_with_hanlder

load_dotenv()


def setup_and_run_bot():
    dp = Dispatcher()
    # step 1 - configure commands and dispatcher
    configure_commands_and_dispatcher(dp)

    # ----------------------------------------------
    # --- start bot-lib part ---
    # ----------------------------------------------

    setup_dispatcher_with_hanlder(dp)

    # ----------------------------------------------
    # --- end bot-lib part ---
    # ----------------------------------------------

    # ----------------------------------------------
    # --- start aiogram part ---
    # ----------------------------------------------

    @dp.message()
    async def echo_handler(message: types.Message) -> None:
        try:
            await message.send_copy(chat_id=message.chat.id)
        except TypeError:
            await message.answer("Nice try!")

    # ----------------------------------------------
    # --- end aiogram part ---
    # ----------------------------------------------

    # step 2 - setup bot
    bot = create_bot()

    # step 3 - run bot
    run_bot(dp, bot)


if __name__ == '__main__':
    setup_and_run_bot()
