from pyrogram import Filters
from asyncio import sleep

from nana import app, Command, AdminSettings
from nana.helpers.expand import expand_url
from nana.helpers.PyroHelpers import msg

__MODULE__ = "Link Expander"
__HELP__ = """
This module will expand your link

──「 **expand url** 」──
-> `expand (link)`
Reply or parse arg of url to expand
"""


@app.on_message(Filters.command("expand", Command) & Filters.user(AdminSettings))
async def expand(_client, message):
    if message.reply_to_message:
        url = message.reply_to_message.text or message.reply_to_message.caption
    elif len(message.command) > 1:
        url = message.command[1]
    else:
        url = None

    if url:
        expanded = await expand_url(url)
        if expanded:
            await msg(message, text=f"<b>Shortened URL</b>: {url}\n<b>Expanded URL</b>: {expanded}", disable_web_page_preview=True)
            return
        else:
            await msg(message, text="`i Cant expand this url :p`")
            await sleep(3)
            await message.delete()
    else:
        await msg(message, text="Nothing to expand")
