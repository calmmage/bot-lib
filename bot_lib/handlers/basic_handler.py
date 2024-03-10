from bot_lib.handlers import Handler, HandlerDisplayMode


class BasicHandler(Handler):
    name = 'basic'
    display_mode = HandlerDisplayMode.FULL
    commands = {
        'start_handler': 'start',
        'help_handler': 'help'
    }

    async def start_handler(self, message):
        await message.answer("start")

    async def help_handler(self, message):
        await message.answer("help")
