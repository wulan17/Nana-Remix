import re
import sre_constants

from pyrogram import Filters

from nana import app


@app.on_message(Filters.me & Filters.regex("^s/(.*?)"))
async def sed_msg(client, message):
    await message.delete()
