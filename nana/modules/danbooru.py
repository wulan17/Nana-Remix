import requests
from asyncio import sleep
from pyrogram import Filters
from nana import app, Command, AdminSettings
from nana.helpers.PyroHelpers import msg
__MODULE__ = "Danbooru"
__HELP__ = """
This module can search images in danbooru and send in to the chat!

──「 **Danbooru Search** 」──
-> `animu`(search string) or `animu nsfw`(search nsfw string)
Search images from Danbooru.

"""

@app.on_message(Filters.user(AdminSettings) & Filters.command("animu", Command))
async def danbooru(client, message):
    await msg(message, text="`Processing…`")

    rating = "Explicit" if "nsfw" in message.command[1] else "Safe"
    search_query = ' '.join(message.command[2:])

    params = {"limit": 1,
              "random": "true",
              "tags": f"Rating:{rating} {search_query}".strip()}

    with requests.get("http://danbooru.donmai.us/posts.json", params=params) as response:
        if response.status_code == 200:
            response = response.json()
        else:
            await msg(message, text=f"`An error occurred, response code:` **{response.status_code}**")
            await sleep(5)
            await message.delete()
            return

    if not response:
        await msg(message, text=f"`No results for query:` __{search_query}__")
        await sleep(5)
        await message.delete()
        return

    valid_urls = [
        response[0][url]
        for url in ['file_url', 'large_file_url', 'source']
        if url in response[0].keys()
    ]


    if not valid_urls:
        await msg(message, text=f"`Failed to find URLs for query:` __{search_query}__")
        await sleep(5)
        await message.delete()
        return
    for image_url in valid_urls:
        try:
            await client.send_photo(message.chat.id, image_url)
            await message.delete()
            return
        except Exception as e:
            print(e)
    await msg(message, text=f"``Failed to fetch media for query:` __{search_query}__")
    await sleep(5)
    await message.delete()