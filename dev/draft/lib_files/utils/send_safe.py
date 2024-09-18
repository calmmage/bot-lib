async def send_safe(chat_id, text, **kwargs):
    """
    Send message with safe mode
    :param chat_id:
    :param text:
    :param kwargs:
    :return:
    """
    # bot =
    await bot.send_message(chat_id, text, **kwargs)