import random
from asyncio import sleep
from pyrogram import Filters
from nana import app, Command, AdminSettings
from nana.helpers.PyroHelpers import msg

__MODULE__ = "Quotly"
__HELP__ = """
This module can make message text to sticker. (Experimental)

──「 **Make Quote From Message** 」──
-> `q`
__Reply To Message Text To Create Quote Sticker.__

"""


@app.on_message(Filters.user(AdminSettings) & Filters.command("q", Command))
async def q_maker(_client, message):
    if not message.reply_to_message:
        await msg(message, text="**Reply to any users text message**")
        return
    await message.reply_to_message.forward("@QuotLyBot")
    is_sticker = False
    while not is_sticker:
        try:
            ms_g = await app.get_history("@QuotLyBot", 1)
            check = ms_g[0]["sticker"]["file_id"]
            print(check)
            is_sticker = True
        except Exception as e:
            print(e)
            await sleep(0.5)
            try:
                await msg(message, text="**Making a Quote**")
            except Exception as e:
                print(e)
    await msg(message, text="**Completed!**")
    msg_id = ms_g[0]["message_id"]
    await message.delete()
    await app.forward_messages(message.chat.id, "@QuotLyBot", msg_id, as_copy=True)
