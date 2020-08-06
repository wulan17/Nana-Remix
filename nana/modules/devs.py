import os
import git
import re
import shutil
import subprocess
import sys
import traceback
from platform import python_version

import requests
from pyrogram import Filters
import pyrogram as p

from nana import Command, logging, app, DB_AVAILABLE, USERBOT_VERSION, AdminSettings
from nana.helpers.deldog import deldog
from nana.helpers.parser import mention_markdown
from nana.helpers.aiohttp_helper import AioHttp
from nana.helpers.PyroHelpers import msg

__MODULE__ = "Devs"
__HELP__ = """
This command means for helping development

──「 **Execution** 」──
-> `py (command)`
Execute a python commands.

──「 **Evaluation** 」──
-> `eval (command)`
Do math evaluation.

──「 **Command shell** 」──
-> `sh (command)`
Execute command shell

──「 **Take log** 」──
-> `log`
Edit log message, or deldog instead

──「 **Get Data Center** 」──
-> `dc`
Get user specific data center

──「 **Test Your Server Internet Speed** 」──
-> `speedtest`
Obtain Server internet speed using speedtest

──「 **Get ID** 」──
-> `id`
Send id of what you replied to

"""


async def stk(chat, photo):
    if "http" in photo:
        r = requests.get(photo, stream=True)
        with open("nana/cache/stiker.png", "wb") as stk:
            shutil.copyfileobj(r.raw, stk)
        await app.send_sticker(chat, "nana/cache/stiker.png")
        os.remove("nana/cache/stiker.png")
    else:
        await app.send_sticker(chat, photo)


async def vid(chat, video, caption=None):
    await app.send_video(chat, video, caption)


async def pic(chat, photo, caption=None):
    await app.send_photo(chat, photo, caption)


async def aexec(client, message, code):
    # Make an async function with the code and `exec` it
    exec(
        'async def __ex(client, message): ' +
        ''.join(f'\n {l}' for l in code.split('\n'))
    )

    # Get `__ex` from local variables, call it and return the result
    return await locals()['__ex'](client, message)


@app.on_message(Filters.me & Filters.command("py", Command))
async def executor(client, message):
    if len(message.text.split()) == 1:
        await msg(message, text="Usage: `py await msg(message, text='edited!')`")
        return
    args = message.text.split(None, 1)
    code = args[1]
    try:
        await aexec(client, message, code)
    except Exception as e:
        print(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        errors = traceback.format_exception(etype=exc_type, value=exc_obj, tb=exc_tb)
        await msg(message, text="**Execute**\n`{}`\n\n**Failed:**\n```{}```".format(code, "".join(errors)))
        logging.exception("Execution error")


@app.on_message(Filters.me & Filters.command("ip", Command))
async def public_ip(_client, message):
    j = await AioHttp().get_json("http://ip-api.com/json")
    stats = f"**ISP {j['isp']}:**\n"
    stats += f"**AS:** `{j['as']}`\n"
    stats += f"**IP Address:** `{j['query']}`\n"
    stats += f"**Country:** `{j['country']}`\n"
    stats += f"**Zip code:** `{j['zip']}`\n"
    stats += f"**Lattitude:** `{j['lat']}`\n"
    stats += f"**Longitude:** `{j['lon']}`\n"
    stats += f"**Time Zone:** `{j['timezone']}`"
    await msg(message, text=stats, parse_mode='markdown')



@app.on_message(Filters.me & Filters.command("sh", Command))
async def terminal(client, message):
    if len(message.text.split()) == 1:
        await msg(message, text="Usage: `sh ping -c 5 google.com`")
        return
    args = message.text.split(None, 1)
    teks = args[1]
    if "\n" in teks:
        code = teks.split("\n")
        output = ""
        for x in code:
            shell = re.split(''' (?=(?:[^'"]|'[^']*'|"[^"]*")*$)''', x)
            try:
                process = subprocess.Popen(
                    shell,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            except Exception as err:
                print(err)
                await msg(message, text="""
**Input:**
```{}```

**Error:**
```{}```
""".format(teks, err))
            output += "**{}**\n".format(code)
            output += process.stdout.read()[:-1].decode("utf-8")
            output += "\n"
    else:
        shell = re.split(''' (?=(?:[^'"]|'[^']*'|"[^"]*")*$)''', teks)
        for a in range(len(shell)):
            shell[a] = shell[a].replace('"', "")
        try:
            process = subprocess.Popen(
                shell,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        except Exception as err:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            errors = traceback.format_exception(etype=exc_type, value=exc_obj, tb=exc_tb)
            await msg(message, text="""**Input:**\n```{}```\n\n**Error:**\n```{}```""".format(teks, "".join(errors)))
            return
        output = process.stdout.read()[:-1].decode("utf-8")
    if str(output) == "\n":
        output = None
    if output:
        if len(output) > 4096:
            file = open("nana/cache/output.txt", "w+")
            file.write(output)
            file.close()
            await client.send_document(message.chat.id, "nana/cache/output.txt", reply_to_message_id=message.message_id,
                                       caption="`Output file`")
            os.remove("nana/cache/output.txt")
            return
        await msg(message, text="""**Input:**\n```{}```\n\n**Output:**\n```{}```""".format(teks, output))
    else:
        await msg(message, text="**Input: **\n`{}`\n\n**Output: **\n`No Output`".format(teks))


@app.on_message(Filters.me & Filters.command(["log"], Command))
async def log(_client, message):
    f = open("nana/logs/error.log", "r")
    data = await deldog(message, f.read())
    await msg(message, text=f"`Your recent logs stored here : `{data}")


@app.on_message(Filters.me & Filters.command("dc", Command))
async def dc_id(_client, message):
    user = message.from_user
    if message.reply_to_message:
        if message.reply_to_message.forward_from:
            dc_id = message.reply_to_message.forward_from.dc_id
            user = mention_markdown(message.reply_to_message.forward_from.id,
                                    message.reply_to_message.forward_from.first_name)
        else:
            dc_id = message.reply_to_message.from_user.dc_id
            user = mention_markdown(message.reply_to_message.from_user.id,
                                    message.reply_to_message.from_user.first_name)
    else:
        dc_id = user.dc_id
        user = mention_markdown(message.from_user.id, message.from_user.first_name)
    if dc_id == 1:
        text = "{}'s assigned datacenter is **DC1**, located in **MIA, Miami FL, USA**".format(user)
    elif dc_id == 2:
        text = "{}'s assigned datacenter is **DC2**, located in **AMS, Amsterdam, NL**".format(user)
    elif dc_id == 3:
        text = "{}'s assigned datacenter is **DC3**, located in **MIA, Miami FL, USA**".format(user)
    elif dc_id == 4:
        text = "{}'s assigned datacenter is **DC4**, located in **AMS, Amsterdam, NL**".format(user)
    elif dc_id == 5:
        text = "{}'s assigned datacenter is **DC5**, located in **SIN, Singapore, SG**".format(user)
    else:
        text = "{}'s assigned datacenter is **Unknown**".format(user)
    await msg(message, text=text)


@app.on_message(Filters.me & Filters.command("alive", Command))
async def alive(_client, message):
    repo = git.Repo(os.getcwd())
    master = repo.head.reference
    commit_id = master.commit.hexsha
    commit_link = f"<a href='https://github.com/pokurt/Nana-Remix/commit/{commit_id}'>{commit_id[:7]}</a>"
    try:
        me = await app.get_me()
    except ConnectionError:
        me = None
    text = f"**[Nana-Remix](https://github.com/pokurt/Nana-Remix) Running on {commit_link}:**\n"
    if not me:
        text += f" - **Bot**: `stopped (v{USERBOT_VERSION})`\n"
    else:
        text += f" - **Bot**: `alive (v{USERBOT_VERSION})`\n"
    text += f" - **Pyrogram**: `{p.__version__}`\n"
    text += f" - **Python**: `{python_version()}`\n"
    text += f" - **Database**: `{DB_AVAILABLE}`\n"
    await msg(message, text=text, disable_web_page_preview=True)

@app.on_message(Filters.me & Filters.command("id", Command))
async def get_id(_client, message):
    file_id = None
    user_id = None
    if message.reply_to_message:
        rep = message.reply_to_message
        if rep.audio:
            file_id = f"**File ID**: `{rep.audio.file_id}`\n"
            file_id += f"**File Ref**: `{rep.audio.file_ref}`\n"
            file_id += "**File Type**: `audio`\n"
        elif rep.document:
            file_id = f"**File ID**: `{rep.document.file_id}`\n"
            file_id += f"**File Ref**: `{rep.document.file_ref}`\n"
            file_id += f"**File Type**: `{rep.document.mime_type}`\n"
        elif rep.photo:
            file_id = f"**File ID**: `{rep.photo.file_id}`\n"
            file_id += f"**File Ref**: `{rep.photo.file_ref}`\n"
            file_id += "**File Type**: `photo`"
        elif rep.sticker:
            file_id = f"**Sicker ID**: `{rep.sticker.file_id}`\n"
            if rep.sticker.set_name and rep.sticker.emoji:
                file_id += f"**Sticker Set**: `{rep.sticker.set_name}`\n"
                file_id += f"**Sticker Emoji**: `{rep.sticker.emoji}`\n"
                if rep.sticker.is_animated:
                    file_id += f"**Animated Sticker**: `{rep.sticker.is_animated}`\n"
                else:
                    file_id += "**Animated Sticker**: `False`\n"
            else:
                file_id += "**Sticker Set**: __None__\n"
                file_id += "**Sticker Emoji**: __None__"
        elif rep.video:
            file_id = f"**File ID**: `{rep.video.file_id}`\n"
            file_id += f"**File Ref**: `{rep.video.file_ref}`\n"
            file_id += "**File Type**: `video`"
        elif rep.animation:
            file_id = f"**File ID**: `{rep.animation.file_id}`\n"
            file_id += f"**File Ref**: `{rep.animation.file_ref}`\n"
            file_id += "**File Type**: `GIF`"
        elif rep.voice:
            file_id = f"**File ID**: `{rep.voice.file_id}`\n"
            file_id += f"**File Ref**: `{rep.voice.file_ref}`\n"
            file_id += "**File Type**: `Voice Note`"
        elif rep.video_note:
            file_id = f"**File ID**: `{rep.animation.file_id}`\n"
            file_id += f"**File Ref**: `{rep.animation.file_ref}`\n"
            file_id += "**File Type**: `Video Note`"
        elif rep.location:
            file_id = "**Location**:\n"
            file_id += f"**longitude**: `{rep.location.longitude}`\n"
            file_id += f"**latitude**: `{rep.location.latitude}`"
        elif rep.venue:
            file_id = "**Location**:\n"
            file_id += f"**longitude**: `{rep.venue.location.longitude}`\n"
            file_id += f"**latitude**: `{rep.venue.location.latitude}`\n\n"
            file_id += "**Address**:\n"
            file_id += f"**title**: `{rep.venue.title}`\n"
            file_id += f"**detailed**: `{rep.venue.address}`\n\n"
        elif rep.from_user:
            user_id = rep.from_user.id
    if user_id:
        if rep.forward_from:
            user_detail = f"**Forwarded User ID**: `{message.reply_to_message.forward_from.id}`\n"
        else:
            user_detail = f"**User ID**: `{message.reply_to_message.from_user.id}`\n"
        user_detail += f"**Message ID**: `{message.reply_to_message.message_id}`"
        await msg(message, text=user_detail)
    elif file_id:
        if rep.forward_from:
            user_detail = f"**Forwarded User ID**: `{message.reply_to_message.forward_from.id}`\n"
        else:
            user_detail = f"**User ID**: `{message.reply_to_message.from_user.id}`\n"
        user_detail += f"**Message ID**: `{message.reply_to_message.message_id}`\n\n"
        user_detail += file_id
        await msg(message, text=user_detail)
    else:
        await msg(message, text=f"**Chat ID**: `{message.chat.id}`")
