import re

from asyncio import sleep
from pyrogram import Filters
from pyrogram.errors import MessageNotModified
from nana import app, Command, AdminSettings
from nana.helpers.PyroHelpers import msg

__MODULE__ = "Vulgar"
__HELP__ = """
Filters Bad Words

──「 **Vulgar Filter** 」──
-> `vulgar`
Turns on & off vulgar filter

Current words: 'nigga', 'nigger', 'coon', 'fuck', 'bitch'

"""

vulgar_filter = False

bad_words = ['nigga', 'nigger', 'coon', 'bitch']
f_word = ['fuck', 'suck']


@app.on_message(~Filters.regex(r"^\.\w*") & Filters.me)
async def vulgar_f(_client, message):
    if not vulgar_filter:
        return
    try:
        txt = None
        if message.caption:
            txt = message.caption
        elif message.text:
            txt = message.text

        for word in bad_words:
            txt = re.sub(word, 'bruh', txt, flags=re.IGNORECASE)

        for word in f_word:
            txt = re.sub(word, 'duck', txt, flags=re.IGNORECASE)

        if message.caption:
            if txt != message.caption:
                await message.edit_caption(txt)
        elif message.text:
            if txt != message.text:
                await message.edit(txt)
    except MessageNotModified:
        return


@app.on_message(Filters.user(AdminSettings) & Filters.command("vulgar", Command))
async def vulgar_trigger(_client, message):
    global vulgar_filter
    if vulgar_filter:
        vulgar_filter = False
        await msg(message, text="Message will not be filtered")
    else:
        vulgar_filter = True
        await msg(message, text="Message will be filtered")
    await sleep(5)
    await message.delete()