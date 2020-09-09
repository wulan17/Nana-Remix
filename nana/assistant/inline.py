import sys
import traceback
import random
import requests
import git
import os
from datetime import datetime
from pyrogram import errors, __version__
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputTextMessageContent, InlineQueryResultArticle, InlineQueryResultPhoto
from pyrogram.errors import PeerIdInvalid
from platform import python_version

from nana import setbot, Owner, OwnerName, DB_AVAILABLE, app, USERBOT_VERSION, AdminSettings
from nana.helpers.msg_types import Types
from nana.helpers.string import parse_button, build_keyboard
from nana.modules.pm import welc_txt
from nana.helpers.aiohttp_helper import AioHttp
from nana.modules.animelist import url, anime_query, shorten
from nana.modules.stylish import text_style_generator, formatting_text_inline, CHAR_OVER, \
    CHAR_UNDER, CHAR_STRIKE, graffiti, graffitib, CHAR_POINTS, upsidedown_text_inline, smallcaps, superscript, \
    subscript, wide, bubbles, bubblesblack, smothtext, handwriting, handwritingb

if DB_AVAILABLE:
    from nana.modules.database import notes_db

# TODO: Add more inline query
# TODO: Wait for pyro update to add more inline query
GET_FORMAT = {
    Types.TEXT.value: InlineQueryResultArticle,
    # Types.DOCUMENT.value: InlineQueryResultDocument,
    Types.PHOTO.value: InlineQueryResultPhoto,
    # Types.VIDEO.value: InlineQueryResultVideo,
    # Types.STICKER.value: InlineQueryResultCachedSticker,
    # Types.AUDIO.value: InlineQueryResultAudio,
    # Types.VOICE.value: InlineQueryResultVoice,
    # Types.VIDEO_NOTE.value: app.send_video_note,
    # Types.ANIMATION.value: InlineQueryResultGif,
    # Types.ANIMATED_STICKER.value: InlineQueryResultCachedSticker,
    # Types.CONTACT: InlineQueryResultContact
}


@setbot.on_inline_query()
async def inline_query_handler(client, query):
    string = query.query.lower()
    answers = []

    if query.from_user.id not in AdminSettings:
        await client.answer_inline_query(query.id,
                                         results=answers,
                                         switch_pm_text="Sorry, this bot only for {}".format(OwnerName),
                                         switch_pm_parameter="createown"
                                         )
        return

    if string == "":
        await client.answer_inline_query(query.id,
                                         results=answers,
                                         switch_pm_text="Need help? Click here",
                                         switch_pm_parameter="help_inline"
                                         )
        return

    # Notes
    if string.split()[0] == "note":
        if not DB_AVAILABLE:
            await client.answer_inline_query(query.id,
                                             results=answers,
                                             switch_pm_text="Your database isn't avaiable!",
                                             switch_pm_parameter="help_inline"
                                             )
            return
        if len(string.split()) == 1:
            allnotes = notes_db.get_all_selfnotes_inline(query.from_user.id)
            if not allnotes:
                await client.answer_inline_query(query.id,
                                                 results=answers,
                                                 switch_pm_text="You dont have any notes!",
                                                 switch_pm_parameter="help_inline"
                                                 )
                return
            if len(list(allnotes)) >= 30:
                rng = 30
            else:
                rng = len(list(allnotes))
            for x in range(rng):
                note = allnotes[list(allnotes)[x]]
                noteval = note["value"]
                notetype = note["type"]
                # notefile = note["file"]
                if notetype != Types.TEXT:
                    continue
                note, button = parse_button(noteval)
                button = build_keyboard(button)
                answers.append(InlineQueryResultArticle(
                    title="Note #{}".format(list(allnotes)[x]),
                    description=note,
                    input_message_content=InputTextMessageContent(note),
                    reply_markup=InlineKeyboardMarkup(button)))
            await client.answer_inline_query(query.id,
                                             results=answers,
                                             switch_pm_text="Yourself notes",
                                             switch_pm_parameter="help_inline"
                                             )
            return
        q = string.split(None, 1)
        notetag = q[1]
        noteval = notes_db.get_selfnote(query.from_user.id, notetag)
        if not noteval:
            await client.answer_inline_query(query.id,
                                             results=answers,
                                             switch_pm_text="Note not found!",
                                             switch_pm_parameter="help_inline"
                                             )
            return
        note, button = parse_button(noteval.get('value'))
        button = build_keyboard(button)
        answers.append(InlineQueryResultArticle(
            title="Note #{}".format(notetag),
            description=note,
            input_message_content=InputTextMessageContent(note),
            reply_markup=InlineKeyboardMarkup(button)))
        try:
            await client.answer_inline_query(query.id,
                                             results=answers,
                                             cache_time=5
                                             )
        except errors.exceptions.bad_request_400.MessageEmpty:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            log_errors = traceback.format_exception(etype=exc_type, value=exc_obj, tb=exc_tb)
            button = InlineKeyboardMarkup([[InlineKeyboardButton("🐞 Report bugs", callback_data="report_errors")]])
            text = "An error has accured!\n\n```{}```\n".format("".join(log_errors))
            await setbot.send_message(Owner, text, reply_markup=button)
            return

    # Stylish converter

    elif string.split()[0] == "stylish":
        if len(string.split()) == 1:
            await client.answer_inline_query(query.id,
                                             results=answers,
                                             switch_pm_text="Insert any text to convert it!",
                                             switch_pm_parameter="help_inline"
                                             )
            return
        text = string.split(None, 1)[1]
        upside = upsidedown_text_inline(text)
        answers.append(InlineQueryResultArticle(
            title=upside,
            description="Upside-down Text",
            input_message_content=InputTextMessageContent(upside)))
        over = text_style_generator(text, CHAR_OVER)
        answers.append(InlineQueryResultArticle(
            title=over,
            description="Overline Text",
            input_message_content=InputTextMessageContent(over)))
        under = text_style_generator(text, CHAR_UNDER)
        answers.append(InlineQueryResultArticle(
            title=under,
            description="Underline Text",
            input_message_content=InputTextMessageContent(under)))
        strike = text_style_generator(text, CHAR_STRIKE)
        answers.append(InlineQueryResultArticle(
            title=strike,
            description="Strike Text",
            input_message_content=InputTextMessageContent(strike)))
        points = text_style_generator(text, CHAR_POINTS)
        answers.append(InlineQueryResultArticle(
            title=points,
            description="Points Text",
            input_message_content=InputTextMessageContent(points)))
        smallcaps_conv = formatting_text_inline(text, smallcaps)
        answers.append(InlineQueryResultArticle(
            title=smallcaps_conv,
            description="Smallcaps Text",
            input_message_content=InputTextMessageContent(smallcaps_conv)))
        super_script = formatting_text_inline(text, superscript)
        answers.append(InlineQueryResultArticle(
            title=super_script,
            description="Superscript Text",
            input_message_content=InputTextMessageContent(super_script)))
        sub_script = formatting_text_inline(text, subscript)
        answers.append(InlineQueryResultArticle(
            title=sub_script,
            description="Subscript Text",
            input_message_content=InputTextMessageContent(sub_script)))
        wide_text = formatting_text_inline(text, wide)
        answers.append(InlineQueryResultArticle(
            title=wide_text,
            description="Wide Text",
            input_message_content=InputTextMessageContent(wide_text)))
        bubbles_text = formatting_text_inline(text, bubbles)
        answers.append(InlineQueryResultArticle(
            title=bubbles_text,
            description="Bubbles Text",
            input_message_content=InputTextMessageContent(bubbles_text)))
        bubblesblack_text = formatting_text_inline(text, bubblesblack)
        answers.append(InlineQueryResultArticle(
            title=bubblesblack_text,
            description="Bubbles Black Text",
            input_message_content=InputTextMessageContent(bubblesblack_text)))
        smoth_text = formatting_text_inline(text, smothtext)
        answers.append(InlineQueryResultArticle(
            title=smoth_text,
            description="Smoth Text",
            input_message_content=InputTextMessageContent(smoth_text)))

        graffiti_text = formatting_text_inline(text, graffiti)
        answers.append(InlineQueryResultArticle(
            title=graffiti_text,
            description="Graffiti Text",
            input_message_content=InputTextMessageContent(graffiti_text)))
        graffitib_text = formatting_text_inline(text, graffitib)
        answers.append(InlineQueryResultArticle(
            title=graffitib_text,
            description="Graffiti Bold Text",
            input_message_content=InputTextMessageContent(graffitib_text)))
        handwriting_text = formatting_text_inline(text, handwriting)
        answers.append(InlineQueryResultArticle(
            title=handwriting_text,
            description="Handwriting Text",
            input_message_content=InputTextMessageContent(handwriting_text)))
        handwritingb_text = formatting_text_inline(text, handwritingb)
        answers.append(InlineQueryResultArticle(
            title=handwritingb_text,
            description="Handwriting Bold Text",
            input_message_content=InputTextMessageContent(handwritingb_text)))
        await client.answer_inline_query(query.id,
                                         results=answers,
                                         switch_pm_text="Converted to stylish text",
                                         switch_pm_parameter="help_inline"
                                         )

    # PM_PERMIT
    elif string.split()[0] == "engine_pm":
        button = [[InlineKeyboardButton("Ask for Money", callback_data="engine_pm_block"),
                   InlineKeyboardButton("Contact me", callback_data="engine_pm_nope")],
                  [InlineKeyboardButton("Report", callback_data="engine_pm_report"),
                   InlineKeyboardButton("Passing by", callback_data="engine_pm_none")]]
        random.shuffle(button)
        answers.append(InlineQueryResultArticle(
            title="Engine pm",
            description="Filter pm",
            input_message_content=InputTextMessageContent(welc_txt, parse_mode="markdown"),
            reply_markup=InlineKeyboardMarkup(button)))
        await client.answer_inline_query(query.id,
                                         results=answers,
                                         cache_time=0
                                         )

    elif string.split()[0] == "speedtest":
        buttons = [[InlineKeyboardButton("Image",
                                        callback_data="speedtest_image"),
                    InlineKeyboardButton("Text",
                                        callback_data="speedtest_text")]]
        answers.append(InlineQueryResultArticle(
            title="Speed Test",
            description="test your speed",
            input_message_content=InputTextMessageContent("Select SpeedTest Mode", parse_mode="markdown"),
            reply_markup=InlineKeyboardMarkup(buttons)))
        await client.answer_inline_query(query.id,
                                         results=answers,
                                         cache_time=0
                                         )
    elif string.split()[0] == "alive":
        repo = git.Repo(os.getcwd())
        master = repo.head.reference
        commit_id = master.commit.hexsha
        commit_link = f"[{commit_id[:7]}](https://github.com/wulan17/Nana-Remix/commit/{commit_id})"
        try:
            me = await app.get_me()
        except ConnectionError:
            me = None
        text = f"**[Nana-Remix](https://github.com/wulan17/Nana-Remix) Running on {commit_link}:**\n"
        if not me:
            text += f" - **Bot**: `stopped (v{USERBOT_VERSION})`\n"
        else:
            text += f" - **Bot**: `alive (v{USERBOT_VERSION})`\n"
        text += f" - **Pyrogram**: `{__version__}`\n"
        text += f" - **Python**: `{python_version()}`\n"
        text += f" - **Database**: `{DB_AVAILABLE}`\n"
        buttons = [[InlineKeyboardButton("stats", callback_data="alive_message")]]
        answers.append(InlineQueryResultArticle(
            title="Alive",
            description="Nana Userbot",
            input_message_content=InputTextMessageContent(text, parse_mode="markdown", disable_web_page_preview=True),
            reply_markup=InlineKeyboardMarkup(buttons)))
        await client.answer_inline_query(query.id,
                                         results=answers,
                                         cache_time=0
                                         )
    elif string.split()[0] == "anime":
        if len(string.split()) == 1:
            await client.answer_inline_query(query.id,
                                             results=answers,
                                             switch_pm_text="Search an Anime",
                                             switch_pm_parameter="help_inline"
                                             )
            return
        search = string.split(None, 1)[1]
        variables = {'search' : search}
        json = requests.post(url, json={'query': anime_query, 'variables': variables}).json()['data'].get('Media', None)
        if json:
            msg = f"**{json['title']['romaji']}** (`{json['title']['native']}`)\n**Type**: {json['format']}\n**Status**: {json['status']}\n**Episodes**: {json.get('episodes', 'N/A')}\n**Duration**: {json.get('duration', 'N/A')} Per Ep.\n**Score**: {json['averageScore']}\n**Genres**: `"
            for x in json['genres']: 
                msg += f"{x}, "
            msg = msg[:-2] + '`\n'
            msg += "**Studios**: `"
            for x in json['studios']['nodes']:
                msg += f"{x['name']}, " 
            msg = msg[:-2] + '`\n'
            info = json.get('siteUrl')
            trailer = json.get('trailer', None)
            if trailer:
                trailer_id = trailer.get('id', None)
                site = trailer.get('site', None)
                if site == "youtube": trailer = 'https://youtu.be/' + trailer_id
            description = json.get('description', 'N/A').replace('<i>', '').replace('</i>', '').replace('<br>', '')
            msg += shorten(description, info) 
            image = json.get('bannerImage', None)
            if trailer:
                buttons = [
                    [InlineKeyboardButton("More Info", url=info),
                    InlineKeyboardButton("Trailer 🎬", url=trailer)]
                    ]
            else:
                buttons = [
                    [InlineKeyboardButton("More Info", url=info)]
                    ]
            if image:
                answers.append(InlineQueryResultPhoto(
                    caption=msg,
                    photo_url=image,
                    parse_mode="markdown",
                    title=f"{json['title']['romaji']}",
                    description=f"{json['format']}",
                    reply_markup=InlineKeyboardMarkup(buttons)))
                await client.answer_inline_query(query.id,
                                                results=answers,
                                                cache_time=0
                                                )
            else:
                answers.append(InlineQueryResultArticle(
                    title=f"{json['title']['romaji']}",
                    description=f"{json['averageScore']}",
                    input_message_content=InputTextMessageContent(msg, parse_mode="markdown", disable_web_page_preview=True),
                    reply_markup=InlineKeyboardMarkup(buttons)))
                await client.answer_inline_query(query.id,
                                                results=answers,
                                                cache_time=0
                                                )

    elif string.split()[0] == "cat":
        image = f"https://d2ph5fj80uercy.cloudfront.net/0{random.randint(1, 6)}/cat{random.randint(0,4999)}.jpg"
        buttons = [[InlineKeyboardButton("Source", url="https://thiscatdoesnotexist.com/")]]
        answers.append(InlineQueryResultPhoto(
                caption='Hi I like you too >~<',
                photo_url=image,
                parse_mode="markdown",
                title="Cursed Cat",
                description="Cursed Cat",
                reply_markup=InlineKeyboardMarkup(buttons)))
        await client.answer_inline_query(query.id,
                                        results=answers,
                                        cache_time=0
                                        )

    if string.split()[0] == "lookup":
        if len(string.split()) == 1:
            await client.answer_inline_query(query.id,
                                             results=answers,
                                             switch_pm_text="Search in SpamProtection Database",
                                             switch_pm_parameter="help_inline"
                                             )
        get_user = string.split(None, 1)[1]
        try:
            user = await app.get_chat(get_user)
        except PeerIdInvalid:
            await client.answer_inline_query(query.id,
                                             results=answers,
                                             switch_pm_text="Can't Find the Chat in Database",
                                             switch_pm_parameter="help_inline"
                                             )
            return
        api_url = f'https://api.intellivoid.net/spamprotection/v1/lookup?query={user.id}'
        a = await AioHttp().get_json(api_url)
        response = a['success']
        if response == True:
            date = a["results"]["last_updated"]
            stats = f'**◢ Intellivoid• SpamProtection Info**:\n'
            stats += f' - **Updated on**: `{datetime.fromtimestamp(date).strftime("%Y-%m-%d %I:%M:%S %p")}`\n'
            if a["results"]["attributes"]["is_potential_spammer"] == True:
                stats += f' - **User**: `USERxSPAM`\n'
            elif a["results"]["attributes"]["is_operator"] == True:
                stats += f' - **User**: `USERxOPERATOR`\n'
            elif a["results"]["attributes"]["is_agent"] == True:
                stats += f' - **User**: `USERxAGENT`\n'
            elif a["results"]["attributes"]["is_whitelisted"] == True:
                stats += f' - **User**: `USERxWHITELISTED`\n'
        
            stats += f' - **Type**: `{a["results"]["entity_type"]}`\n'
            stats += f' - **Language**: `{a["results"]["language_prediction"]["language"]}`\n'
            stats += f' - **Language Probability**: `{a["results"]["language_prediction"]["probability"]}`\n'
            stats += f'**Spam Prediction**:\n'
            stats += f' - **Ham Prediction**: `{a["results"]["spam_prediction"]["ham_prediction"]}`\n'
            stats += f' - **Spam Prediction**: `{a["results"]["spam_prediction"]["spam_prediction"]}`\n'
            stats += f'**Blacklisted**: `{a["results"]["attributes"]["is_blacklisted"]}`\n'
            if a["results"]["attributes"]["is_blacklisted"] == True:
                stats += f' - **Reason**: `{a["results"]["attributes"]["blacklist_reason"]}`\n'
                stats += f' - **Flag**: `{a["results"]["attributes"]["blacklist_flag"]}`\n'
            stats += f'**TELEGRAM HASH**:\n`{a["results"]["private_telegram_id"]}`\n'
        buttons = [[InlineKeyboardButton("Logs", url="https://t.me/SpamProtectionLogs"),
                    InlineKeyboardButton('Info', url=f't.me/SpamProtectionBot/?start=00_{user.id}')]]
        answers.append(InlineQueryResultArticle(
            title=f'{a["results"]["entity_type"]}',
            description=f'{a["results"]["private_telegram_id"]}',
            input_message_content=InputTextMessageContent(stats, parse_mode="markdown", disable_web_page_preview=True),
            reply_markup=InlineKeyboardMarkup(buttons)))
        await client.answer_inline_query(query.id,
                                        results=answers,
                                        cache_time=0
                                        )
        return