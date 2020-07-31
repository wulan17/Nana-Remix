import requests
from asyncio import sleep

from nana import app, Command, AdminSettings
from pyrogram import Filters
from nana.helpers.PyroHelpers import msg

__MODULE__ = "Device"
__HELP__ = """
Take a picture of website. You can select one for use this.

──「 **Device** 」──
-> `device (codename)`

Usage: `device (codename)`

"""

DEVICE_LIST = "https://raw.githubusercontent.com/androidtrackers/certified-android-devices/master/by_device.json"


@app.on_message(Filters.user(AdminSettings) & Filters.command("device", Command))
async def get_device(_client, message):
    if len(message.text.split()) == 1:
        await msg(message, text="Usage: `device (codename)`")
        return
    getlist = requests.get(DEVICE_LIST).json()
    target_device = message.text.split()[1].lower()
    if target_device in list(getlist):
        device = getlist.get(target_device)
        text = ""
        for x in device:
            text += f"Brand: `{x['brand']}`\nName: `{x['name']}`\nDevice: `{x['model']}`\nCodename: `{target_device}`"
            text += "\n\n"
        await msg(message, text=text)
    else:
        await msg(message, text=f"Device {target_device} was not found!")
        await sleep(5)
        await message.delete()
