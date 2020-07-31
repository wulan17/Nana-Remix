import os
import shutil

import requests
from pyrogram import Filters

from nana import app, Command, thumbnail_API, screenshotlayer_API, AdminSettings
from nana.helpers.PyroHelpers import msg

__MODULE__ = "SS Website"
__HELP__ = """
Take a picture of website. You can select one for use this.

──「 **Take ss website** 」──
-> `print (url)`
Send web screenshot, not full webpage. Send as picture

──「 **Take ss website (more)** 」──
-> `ss (url) (*full)`
Take screenshot of that website, if `full` args given, take full of website and send image as document

* = optional
"""


@app.on_message(Filters.user(AdminSettings) & Filters.command("print", Command))
async def print_web(client, message):
    if len(message.text.split()) == 1:
        await msg(message, text="Usage: `print web.url`")
        return
    if not thumbnail_API:
        await msg(message, text="You need to fill thumbnail_API to use this!")
        return
    await msg(message, text="Please wait...")
    args = message.text.split(None, 1)
    teks = args[1]
    teks = teks if "http://" in teks or "https://" in teks else "http://" + teks
    capt = f"Website: `{teks}`"

    await client.send_chat_action(message.chat.id, action="upload_photo")
    r = requests.get(f"https://api.thumbnail.ws/api/{thumbnail_API}/thumbnail/get?url={teks}&width=1280",
                     stream=True
                     )
    if r.status_code != 200:
        await msg(message, text=r.text, disable_web_page_preview=True)
        return
    with open("nana/cache/web.png", "wb") as stk:
        shutil.copyfileobj(r.raw, stk)
    await client.send_photo(message.chat.id, photo="nana/cache/web.png", caption=capt,
                            reply_to_message_id=message.message_id)
    os.remove("nana/cache/web.png")
    await client.send_chat_action(message.chat.id, action="cancel")
    msg(message, text=capt)


@app.on_message(Filters.user(AdminSettings) & Filters.command("ss", Command))
async def ss_web(client, message):
    if len(message.text.split()) == 1:
        await msg(message, text="Usage: `print web.url`")
        return
    if not screenshotlayer_API:
        await msg(message, text="You need to fill screenshotlayer_API to use this!")
        return
    await msg(message, text="Please wait...")
    args = message.text.split(None, 1)
    teks = args[1]
    full = False
    if (
        len(message.text.split()) >= 3
        and message.text.split(None, 2)[2] == "full"
    ):
        full = True

    teks = teks if "http://" in teks or "https://" in teks else "http://" + teks
    capt = f"Website: `{teks}`"

    await client.send_chat_action(message.chat.id, action="upload_photo")
    if full:
        r = requests.get(
            f"http://api.screenshotlayer.com/api/capture?access_key={screenshotlayer_API}&url={teks}&fullpage=1",
            stream=True)
    else:
        r = requests.get(
            f"http://api.screenshotlayer.com/api/capture?access_key={screenshotlayer_API}&url={teks}&fullpage=0",
            stream=True)

    try:
        catcherror = r.json()
        if not catcherror['success']:
            await msg(message, text=r.json(), disable_web_page_preview=True)
            return
    except Exception as err:
        print(err)
    with open("nana/cache/web.png", "wb") as stk:
        for chunk in r:
            stk.write(chunk)

    await client.send_document(message.chat.id, document="nana/cache/web.png", caption=capt,
                               reply_to_message_id=message.message_id
                               )
    os.remove("nana/cache/web.png")
    await client.send_chat_action(message.chat.id, action="cancel")
    await msg(message, text=capt)
