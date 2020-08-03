from pyrogram import Filters
from nana import setbot, app, AdminSettings
import speedtest
import re

def speedtest_callback(_, query):
    if re.match("speedtest", query.data):
        return True

speedtest_create = Filters.create(speedtest_callback)

def convert(speed):
    return round(int(speed) / 1048576, 2)

@setbot.on_callback_query(speedtest_create)
async def speedtestxyz_callback(client, query):
    if query.from_user.id in AdminSettings:
        msg = await setbot.edit_inline_text(query.inline_message_id,'Runing a speedtest....')
        speed = speedtest.Speedtest()
        speed.get_best_server()
        speed.download()
        speed.upload()
        replymsg = 'SpeedTest Results:'
        if query.data == 'speedtest_image':
            speedtest_image = speed.results.share()
            await app.send_photo(query.chat.id,
                photo=speedtest_image, caption=replymsg)
            msg.delete()

        elif query.data == 'speedtest_text':
            result = speed.results.dict()
            replymsg += f"\nDownload: `{convert(result['download'])}Mb/s`\nUpload: `{convert(result['upload'])}Mb/s`\nPing: `{result['ping']}`"
            await setbot.edit_inline_text(query.inline_message_id, replymsg, parse_mode="markdown")
    else:
        await client.answer_callback_query(query.id, "No, you are not allowed to do this", show_alert=False)