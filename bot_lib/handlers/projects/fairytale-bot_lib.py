from collections import defaultdict
from functools import wraps
from textwrap import dedent

from aiogram import Bot
from aiogram.enums import ChatAction
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from dotenv import load_dotenv
from loguru import logger
from bot_lib import App, Handler, HandlerDisplayMode

from fairytale_bot.fairytale_settings import FairytaleSettings
from fairytale_bot.user_settings import UserSettings, StoryCompression

load_dotenv()


class MainHandler(Handler):
    name = "main"
    display_mode = HandlerDisplayMode.FULL
    commands = {
        # "custom_handler": "custom",
        # "gpt_complete_handler": ["gpt_complete", "gpt"],
        # "fairytale_handler": "fairytale",
        "randomize_handler": "randomize",
        "generate_next_story_part_handler": [
            "continue",
            "next",
            "generate_next_story_part",
        ],
    }

    # def __init__(self):
    #     super().__init__()

    async def randomize_handler(self, message: Message, app: MainApp, bot: Bot):
        user = self.get_user(message)

        moral = app.get_random_moral()
        app.set_moral(moral, user)
        topic = app.get_random_topic()
        app.set_topic(topic, user)
        author = app.get_random_author()
        app.set_author(author, user)
        response_text = dedent(
            f"""
            Moral set to {moral}
            Topic set to {topic}
            Author set to {author}
            """
        )
        await message.answer(response_text)
        story_structure = await app.generate_story_structure(
            # topic, moral, author,
            user
        )
        # precalc
        app.set_story_structure(user=user, story_structure=story_structure)
        # start generating the story right away - why wait?
        temp_message_text = "Generating the next part of the story..."
        # send typing action
        temp_message = await message.answer(temp_message_text)
        await self.generate_next_story_part_handler(message, app, bot)
        await temp_message.delete()

    async def generate_next_story_part_handler(self, message: Message, app: MainApp, bot: Bot):
        """
        Generate the next story part
        """
        user = self.get_user(message)
        # check usage

        # todo: if this is the first part
        #  - notify the user of the parameters of the generation

        # todo: add emoji - 'generating' - ⌛ - extract id from message via debug
        # temp_message_text = "Generating the next part of the story..."
        # temp_message = await message.answer(temp_message_text)

        chat_id = message.chat.id
        # set bot typing effect
        await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        try:
            response_text = ""
            response_text += await app.generate_next_story_part(user)

            response_text += "\n\n/continue ..."
            await message.answer(response_text)
            app.count_user_usage(user)
        except Exception as e:
            error_message = "Failed, sorry :("
            await message.answer(error_message)
        # await temp_message.delete()
        # unset bot typing effect
        # todo: test if i need to do that?
        # bot.send_chat_action(message.chat.id, action=ChatAction.)

    async def reset_handler(self, message: Message, app: MainApp):
        user = self.get_user(message)
        app.reset(user)
        response_text = "Story reset."
        await message.answer(response_text)

    commands["reset_handler"] = "reset"

    # @staticmethod
    # def strip_command(text: str):
    #     if text.startswith("/"):
    #         parts = text.split(" ", 1)
    #         if len(parts) > 1:
    #             return parts[1].strip()
    #         return ""

    async def archive_handler(self, message: Message, app: MainApp):
        user = self.get_user(message)
        # await self._extract_message_text(message) - support voice messages?
        text = self.strip_command(message.text)
        if text and text.isdigit():
            index = int(text) - 1
            story = app.story_archive[user][index]
            story_text = "\n\n".join(story["story"])
            await self._send_as_file(
                chat_id=message.chat.id,
                text=story_text,
                filename=f"story_{text}.txt",
            )
        else:
            N = len(app.story_archive[user])
            response_text = f"Your archive contains {N} stories. " "Use /archive i to view the i-th story."
            await message.answer(response_text)
