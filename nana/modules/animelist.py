import math
import time
import requests
import json
import asyncio

from pyrogram import Filters


from nana import app, Command, AdminSettings
from nana.helpers.string import replace_text
from nana.helpers.PyroHelpers import msg


__MODULE__ = "Anilist"

__HELP__ = """
Get information about anime, manga or characters from [Anilist](https://anilist.co).

──「 **Anime** 」──
-> `anime <anime>`
returns information about the anime.

__Original Module by @Zero_cooll7870__

──「 **Character** 」──
-> `character <character>`
returns information about the character.

──「 **Manga** 」──
-> `manga <manga>`
returns information about the manga.

──「 **Airing** 」──
-> `airing <anime>`
To get airing time of the anime.

"""


def shorten(description, info='anilist.co'):
    msg = ""
    if len(description) > 700:
        description = description[0:500] + '....'
        msg += f"\n**Description**: __{description}__[Read More]({info})"
    else:
        msg += f"\n**Description**: __{description}__"
    return (
        msg.replace("<br>", "")
        .replace("</br>", "")
        .replace("<i>", "")
        .replace("</i>", "")
    )


# time formatter from uniborg
def t(milliseconds: int) -> str:
    """Inputs time in milliseconds, to get beautified time,
    as string"""
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + " Days, ") if days else "") + \
        ((str(hours) + " Hours, ") if hours else "") + \
        ((str(minutes) + " Minutes, ") if minutes else "") + \
        ((str(seconds) + " Seconds, ") if seconds else "") + \
        ((str(milliseconds) + " ms, ") if milliseconds else "")
    return tmp[:-2]


airing_query = '''
    query ($id: Int,$search: String) { 
      Media (id: $id, type: ANIME,search: $search) { 
        id
        episodes
        title {
          romaji
          english
          native
        }
        nextAiringEpisode {
           airingAt
           timeUntilAiring
           episode
        } 
      }
    }
    '''

fav_query = """
query ($id: Int) { 
      Media (id: $id, type: ANIME) { 
        id
        title {
          romaji
          english
          native
        }
     }
}
"""

anime_query = '''
   query ($id: Int,$search: String) { 
      Media (id: $id, type: ANIME,search: $search) { 
        id
        title {
          romaji
          english
          native
        }
        description (asHtml: false)
        startDate{
            year
          }
          episodes
          season
          type
          format
          status
          duration
          siteUrl
          studios{
              nodes{
                   name
              }
          }
          trailer{
               id
               site 
               thumbnail
          }
          averageScore
          genres
          bannerImage
      }
    }
'''
character_query = """
    query ($query: String) {
        Character (search: $query) {
               id
               name {
                     first
                     last
                     full
               }
               siteUrl
               image {
                        large
               }
               description
        }
    }
"""

manga_query = """
query ($id: Int,$search: String) { 
      Media (id: $id, type: MANGA,search: $search) { 
        id
        title {
          romaji
          english
          native
        }
        description (asHtml: false)
        startDate{
            year
          }
          type
          format
          status
          siteUrl
          averageScore
          genres
          bannerImage
      }
    }
"""


url = 'https://graphql.anilist.co'


@app.on_message(Filters.user(AdminSettings) & Filters.command("airing", Command))
async def anime_airing(_client, message):
    search_str = message.text.split(' ', 1)
    if len(search_str) == 1:
        await msg(message, text='Format: `airing <anime name>`')
        return
    variables = {'search': search_str[1]}
    response = requests.post(
        url, json={'query': airing_query, 'variables': variables}).json()['data']['Media']
    ms_g = f"**Name**: **{response['title']['romaji']}**(`{response['title']['native']}`)\n**ID**: `{response['id']}`"
    if response['nextAiringEpisode']:
        time = response['nextAiringEpisode']['timeUntilAiring'] * 1000
        time = t(time)
        ms_g += f"\n**Episode**: `{response['nextAiringEpisode']['episode']}`\n**Airing In**: `{time}`"
    else:
        ms_g += f"\n**Episode**:{response['episodes']}\n**Status**: `N/A`"
    await msg(message, text=ms_g)


@app.on_message(Filters.user(AdminSettings) & Filters.command("anime", Command))
async def anime_search(client, message):
    search = message.text.split(' ', 1)
    if len(search) == 1:
        await message.delete()
        return
    else:
        search = search[1]
    variables = {'search': search}
    json = requests.post(url, json={'query': anime_query, 'variables': variables}).json()[
        'data'].get('Media', None)
    if json:
        ms_g = f"**{json['title']['romaji']}**(`{json['title']['native']}`)\n**Type**: {json['format']}\n**Status**: {json['status']}\n**Episodes**: {json.get('episodes', 'N/A')}\n**Duration**: {json.get('duration', 'N/A')} Per Ep.\n**Score**: {json['averageScore']}\n**Genres**: `"
        for x in json['genres']:
            ms_g += f"{x}, "
        ms_g = ms_g[:-2] + '`\n'
        ms_g += "**Studios**: `"
        for x in json['studios']['nodes']:
            ms_g += f"{x['name']}, "
        ms_g = ms_g[:-2] + '`\n'
        info = json.get('siteUrl')
        trailer = json.get('trailer', None)
        if trailer:
            trailer_id = trailer.get('id', None)
            site = trailer.get('site', None)
            if site == "youtube":
                trailer = 'https://youtu.be/' + trailer_id
        description = json.get(
            'description', 'N/A').replace('<i>', '').replace('</i>', '').replace('<br>', '')
        ms_g += shorten(description, info)
        image = json.get('bannerImage', None)
        if trailer:
            ms_g += f"\nTrailer: {trailer}"
        if image:
            try:
                await message.delete()
                await client.send_photo(message.chat.id, photo=image, caption=ms_g)
            except:
                ms_g += f" [〽️]({image})"
                await msg(message, text=ms_g)
        else:
            await msg(message, text=ms_g)


@app.on_message(Filters.user(AdminSettings) & Filters.command("character", Command))
async def character_search(client, message):
    search = message.text.split(' ', 1)
    if len(search) == 1:
        await message.delete()
        return
    search = search[1]
    variables = {'query': search}
    json = requests.post(url, json={'query': character_query, 'variables': variables}).json()[
        'data'].get('Character', None)
    if json:
        ms_g = f"**{json.get('name').get('full')}**(`{json.get('name').get('native')}`)\n"
        description = f"{json['description']}"
        site_url = json.get('siteUrl')
        ms_g += shorten(description, site_url)
        image = json.get('image', None)
        if image:
            image = image.get('large')
            await message.delete()
            await client.send_photo(message.chat.id, photo=image, caption=ms_g)
        else:
            await msg(message, text=ms_g)


@app.on_message(Filters.user(AdminSettings) & Filters.command("manga", Command))
async def manga_search(client, message):
    search = message.text.split(' ', 1)
    if len(search) == 1:
        await message.delete()
        return
    search = search[1]
    variables = {'search': search}
    json = requests.post(url, json={'query': manga_query, 'variables': variables}).json()[
        'data'].get('Media', None)
    ms_g = ''
    if json:
        title, title_native = json['title'].get(
            'romaji', False), json['title'].get('native', False)
        start_date, status, score = json['startDate'].get('year', False), json.get(
            'status', False), json.get('averageScore', False)
        if title:
            ms_g += f"**{title}**"
            if title_native:
                ms_g += f"(`{title_native}`)"
        if start_date:
            ms_g += f"\n**Start Date** - `{start_date}`"
        if status:
            ms_g += f"\n**Status** - `{status}`"
        if score:
            ms_g += f"\n**Score** - `{score}`"
        ms_g += '\n**Genres** - '
        for x in json.get('genres', []):
            ms_g += f"{x}, "
        ms_g = ms_g[:-2]

        image = json.get("bannerImage", False)
        ms_g += f"_{json.get('description', None)}_"
        if image:
            try:
                await message.delete()
                await client.send_photo(message.chat.id, photo=image, caption=ms_g)
            except:
                ms_g += f" [〽️]({image})"
                await msg(message, text=ms_g)
        else:
            await msg(message, text=ms_g)
