import datetime

import pytz
from aiogram import types
from bot_lib import Handler, HandlerDisplayMode
from tzlocal import get_localzone

from outstanding_items_bot.app import MyApp


class MyHandler(Handler):
    name = "main"
    display_mode = HandlerDisplayMode.FULL
    commands = {
        "dummy_command_handler": "dummy_command",
        "some_command_handler": "some_command",
        "delete_item": ["del", "delete"],
        "get_random_item": "get_random",
        "get_all_items": "get_all",
        "set_up_auto_reminders": [
            "remind",
            "reminders",
            "remind_me",
            "remind_every_day",
            "random_reminders",
            "setup_reminders",
        ],
    }

    async def dummy_command_handler(self, message, app: MyApp):
        output_str = app.dummy_command()
        await self.reply_safe(message, output_str)

    # region command example
    async def some_command_handler(self, message, app: MyApp):
        output_str = "This is some command"
        await self.reply_safe(message, output_str)

    # endregion command example

    # region button example
    async def some_button(self, message, app: MyApp):
        # todo: find button example
        pass

    async def some_start_message(self, message, app: MyApp):
        # idea 1: custom text for start message describing how this works
        # - commands
        # - regular messages
        # - buttons
        # idea 2:

        output_str = app.start_message

        await self.reply_safe(message, output_str)

    # ----
    # region features
    # feature 1: set up schedule for reminders
    # feature 2: add item
    async def add_item(self, message, app: MyApp):
        description = await self.get_message_text(message)
        item = app.add_item(description)

        # tell the user item is added - and its key
        output_str = f"Item added and is available with this key: {item.keys[0]}"
        await self.reply_safe(message, output_str)

    # feature 3: ... mark (last) item as done
    # feature 4: get random item
    async def get_random_item(self, message, app: MyApp):
        import random

        all_items = app.get_all_items()
        item = random.choice(all_items)
        output_str = f"Random item: {item.description}"
        await self.reply_safe(message, output_str)

    def format_description(self, item, limit=100):
        # make description one line and cut up to the limit
        return item.description[:limit].replace("\n", " ")

    # feature 5: get all items
    async def get_all_items(self, message, app: MyApp):
        all_items = app.get_all_items()

        output_str = "\n".join([f"{item.keys[0]}: {self.format_description(item)}" for item in all_items])
        await self.reply_safe(message, output_str)

    # feature 6: get item by key
    async def get_item(self, message, app: MyApp):
        key = await self.get_message_text(message)
        item = app.get_item(key)

        if item:
            output_str = f"Item: {item.title}"
        else:
            output_str = f"Item not found by key: {key}"
        await self.reply_safe(message, output_str)

    # feature 7: chat = add item
    has_chat_handler = True

    async def chat_handler(self, message: types.Message, app: MyApp):
        """
        Handle chat messages by determining whether the message is a key
        to an existing item or a description for a new item. If the key exists,
        fetch the item. Otherwise, add a new item with the message as its description.

        Args:
            message (types.Message): The message from the chat.
            app (MyApp): The instance of the application.
        """
        # check if has item
        key = await self.get_message_text(message)
        # if key.startswith("del "):
        #     key = key[4:]
        #     await self.delete_item(message, app)
        if app.has_item(key):
            await self.get_item(message, app)
        else:
            await self.add_item(message, app)

    async def delete_item(self, message, app: MyApp):
        key = await self.get_message_text(message)
        if app.delete_item(key):
            output_str = f"Item deleted: {key}"
        else:
            output_str = f"Item not found by key: {key}"
        await self.reply_safe(message, output_str)

    # 9 am every day - for now in utc
    default_timestamp = "09:00"

    @staticmethod
    def get_full_datetime_for_reminder(target_time: str) -> datetime:
        """Return a full datetime object for the reminder to be set in UTC."""
        local_tz = get_localzone()
        current_date = datetime.now(local_tz).date()
        naive_datetime = datetime.combine(current_date, target_time)
        local_datetime = naive_datetime.replace(tzinfo=local_tz)
        utc_datetime = local_datetime.astimezone(pytz.utc)
        return utc_datetime

    # # Example usage:
    # target_time = time(14, 30)  # 2:30 PM
    # reminder_datetime = get_full_datetime_for_reminder(target_time)
    # print(reminder_datetime)
    # First real feature: set up schedule for reminders
    async def set_up_auto_reminders(self, message, app: MyApp):
        # take user chat id
        chat_id = message.chat.id
        # take user time zone
        # timezone = (
        #     None  # todo: get timezone from user or their location. By default, use server time - and tell it to user
        #
        # )
        timezone = "Europe/Moscow"
        timestamp = await self.get_message_text(message)
        timestamp = self.strip_command(timestamp)
        if timestamp:
            print(timestamp)
            # parse timestamp, into
            raise NotImplementedError
        else:
            # take default
            if app.debug:
                # generate some timestamp compatible
                timestamp = datetime.datetime.now()
                # plus 10 seconds
                timestamp += datetime.timedelta(seconds=3)
            else:
                timestamp = self.default_timestamp
                # todo: parse timestamp into datetime object

        # schedule a job to auto-send random item
        # todo: set up scheduler enabled in env?

        from apscheduler.schedulers.asyncio import AsyncIOScheduler

        scheduler: AsyncIOScheduler = app.scheduler.core
        if app.debug:
            print(timestamp)
            print(timezone)
            scheduler.add_job(
                self._send_random_item,
                "interval",
                seconds=3,
                # start_date=None,
                #                  end_date=None, timezone=None,
                start_date=timestamp,
                timezone=timezone,
                kwargs={"app": app, "chat_id": chat_id},
            )
        else:

            scheduler.add_job(
                self._send_random_item,
                "interval",
                start_date=timestamp,
                timezone=timezone,
                days=1,
                kwargs={"app": app, "chat_id": chat_id},
            )

    async def _send_random_item(self, app: MyApp, chat_id: int):
        import random

        all_items = app.get_all_items()
        item = random.choice(all_items)

        output_str = f"Random item: {item.title}\n{item.description}"

        await self.send_safe(chat_id, output_str)

    async def complete_item(self, message, app: MyApp):
        key = await self.get_message_text(message)
        if app.complete(key):
            output_str = f"Item completed: {key}"
        else:
            output_str = f"Item not found by key: {key}"
        await self.reply_safe(message, output_str)

    # endregion features
    # region - bonus, ai features
    # idea 1: generate short item keys with ai - avoid collisions
    # idea 2: generate item descriptions with ai

    # stupid colision resolution: add a number to the end of the key
    # endregion - bonus, ai features
