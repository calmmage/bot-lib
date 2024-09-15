from bot_lib.handlers import HandlerBase, HandlerDisplayMode


class DevHandler(HandlerBase):
    name = "dev"
    display_mode = HandlerDisplayMode.HELP_MESSAGE

    async def ping_handler(self, message):
        await message.answer("ping")
