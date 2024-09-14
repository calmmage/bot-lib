from aiogram.types import Message
from bot_lib import Handler, HandlerDisplayMode
from calmapp import App

from abstract_tool_user.app import MyApp


class MyHandler(Handler):
    name = "main"
    display_mode = HandlerDisplayMode.FULL
    has_chat_handler = True
    # dict handler_func_name -> command aliases
    commands = {
        "reset_command_handler": ["reset"],
        "tool_handler": ["tool"],
    }

    # region 1 - General, init and stuff
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.chat_handler_ignore_commands = True

    async def tool_handler(self, message, app: App):
        # make gpt call the tool using the user input
        # option 1: using ... gpt agent approach
        # option 2: using ... manual forming of the tool list and request to gpt
        # option 3: just call the app's method
        pass

    # endregion General

    async def chat_handler(self, message: Message, app: App):
        input_str = await self.get_message_text(message)
        response = app.invoke(input_str)
        await self.answer_safe(message, response)

    async def reset_command_handler(self, message: Message, app: MyApp):
        await app.reset()
        await self.answer_safe(message, "Chat history reset.")
