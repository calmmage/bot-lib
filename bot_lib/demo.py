from textwrap import dedent

from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from calmapp import App

from bot_lib.handlers import Handler, BasicHandler, HandlerDisplayMode


def configure_commands_and_dispatcher(dp):
    # All handlers should be attached to the Router (or Dispatcher)

    @dp.message(CommandStart())
    async def command_start_handler(message: Message) -> None:
        await message.answer(f"Hello, {hbold(message.from_user.full_name)}!")

    return dp


def setup_dispatcher_with_demo_handler(dp):
    """
    Idea: register a help command from the handler - manually
    :param dp:
    :return:
    """

    handler = BasicHandler()

    dp.message.register(handler.help_handler, Command("help"))


class FairytaleHandler(Handler):
    name = "fairytale_bot"
    display_mode = HandlerDisplayMode.FULL
    commands = {
        "gpt_complete_handler": ["gpt_complete", "gpt"],
        "fairytale_handler": "fairytale",
    }

    async def gpt_complete_handler(self, message: Message, app: App):
        text = message.text
        response = await app.gpt.complete_text(text)
        # todo: use send_safe util instead
        await message.answer(response)

    fairytale_prompt = dedent(
        """
        Tell a fairytale on a specified topic and fabulate it.
        TOPIC:
        {text}
        """
    )

    # token limit
    FAIRYTALE_TOKEN_LIMIT = 1000

    async def fairytale_handler(self, message: Message, app: App):
        """Tell a fairytale on a specified topic and fabulate it."""
        text = message.text
        prompt = self.fairytale_prompt.format(text=text)
        response = await app.gpt.complete_text(
            prompt, max_tokens=self.FAIRYTALE_TOKEN_LIMIT
        )
        # todo: use send_safe util instead
        await message.answer(response)
