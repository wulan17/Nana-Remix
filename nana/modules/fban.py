import time

from pyrogram import filters
	
from nana import app, Owner, Command, DB_AVAILABLE
if DB_AVAILABLE:
	from nana.modules.database import fban_sql as sql

__MODULE__ = "Fban"
__HELP__ = """
This module can help to bans user from connected federations!

──「 **Federation Ban** 」──
-> `fban <id/username> <reason>`
Bans user from connected federations.
You can reply to the user whom you want to fban or manually pass the username/id.

-> `unfban <id/username> <reason>`
Same as fban but unbans the user

-> `addf <name>`
Adds current group and stores it as <name> in connected federations.
Adding one group is enough for one federation.

-> `delf`
Removes current group from connected federations.

-> `listf`
Lists all connected federations by specified name.
"""

@app.on_message(filters.me & (filters.command("fban", Command)))
async def fban(client,message):
	"""Bans a user from connected federations."""
	if not DB_AVAILABLE:
		await message.edit("Your database is not avaiable!")
		return

	if message.reply_to_message:
		text = (message.text).split(None,1)
		reply_msg = message.reply_to_message
		fban_id = reply_msg.from_user.id
		if len(text) > 1:
			reason = text[1]
		else:
			reason = ''
		user_link = f"[{fban_id}](tg://user?id={fban_id})"
	else:
		text = (message.text).split(None,2)
		fban_id = text[1]
		if len(text) > 2:
			reason = text[2]
		else:
			reason = ''
		user_link = fban_id

	self_user = await client.get_me()

	if fban_id == self_user.id or fban_id == "@" + self_user.username:
		return await message.edit(
			"**Error: This action has been prevented by Nana-Remix self preservation protocols.**"
		)

	if len((fed_list := sql.get_flist())) == 0:
		return await message.edit("**You haven't connected to any federations yet!**")

	await message.edit(f"**Fbanning** {user_link}...")
	failed = []
	total = int(0)

	for i in fed_list:
		total += 1
		chat = int(i.chat_id)
		msg = await client.send_message(chat,f"/fban {user_link} {reason}")
		msg_id = msg.message_id
		time.sleep(2)
		count = 0
		for j in range(5):
			reply = await client.get_messages(chat, (msg_id+j))
			if reply.reply_to_message and reply.reply_to_message.message_id == msg_id:
				if (
					("New FedBan" not in reply.text)
					and ("Starting a federation ban" not in reply.text)
					and ("Start a federation ban" not in reply.text)
					and ("FedBan reason updated" not in reply.text)
				):
					failed.append(i.fed_name)
					break
			count = count+1
		if count == 5:
			failed.append(i.fed_name)
	reason = reason if reason else "Not specified."

	if failed:
		status = f"Failed to fban in {len(failed)}/{total} feds.\n"
		for i in failed:
			status += "• " + i + "\n"
	else:
		status = f"Success! Fbanned in {total} feds."

	await message.edit(
		f"**Fbanned **{user_link}!\n**Reason:** {reason}\n**Status:** {status}"
	)

@app.on_message(filters.me & (filters.command("unfban", Command)))
async def fban(client,message):
	"""Bans a user from connected federations."""
	if not DB_AVAILABLE:
		await message.edit("Your database is not avaiable!")
		return

	if message.reply_to_message:
		text = (message.text).split(None,1)
		reply_msg = message.reply_to_message
		fban_id = reply_msg.from_user.id
		if len(text) > 1:
			reason = text[1]
		else:
			reason = ''
		user_link = f"[{fban_id}](tg://user?id={fban_id})"
	else:
		text = (message.text).split(None,2)
		fban_id = text[1]
		if len(text) > 2:
			reason = text[2]
		else:
			reason = ''
		user_link = fban_id

	self_user = await client.get_me()

	if fban_id == self_user.id or fban_id == "@" + self_user.username:
		return await message.edit("**Wait, that's illegal**")

	if len((fed_list := sql.get_flist())) == 0:
		return await message.edit("**You haven't connected to any federations yet!**")

	await message.edit(f"**Un-fbanning **{user_link}**...**")
	failed = []
	total = int(0)

	for i in fed_list:
		total += 1
		chat = int(i.chat_id)
		msg = await client.send_message(chat,f"/unfban {user_link} {reason}")
		msg_id = msg.message_id
		time.sleep(2)
		count = 0
		for j in range(5):
			reply = await client.get_messages(chat, (msg_id+j))
			if reply.reply_to_message and reply.reply_to_message.message_id == msg_id:
				if (
					("New un-FedBan" not in reply.text)
					and ("I'll give" not in reply.text)
					and ("Un-FedBan" not in reply.text)
				):
					failed.append(i.fed_name)
					break
			count = count+1
		if count == 5:
			failed.append(i.fed_name)

	reason = reason if reason else "Not specified."

	if failed:
		status = f"Failed to un-fban in {len(failed)}/{total} feds.\n"
		for i in failed:
			status += "• " + i + "\n"
	else:
		status = f"Success! Un-fbanned in {total} feds."

	await message.edit(
		f"**Un-fbanned** {user_link}!\n**Reason:** {reason}\n**Status:** {status}"
	)

@app.on_message(filters.me & (filters.command("addf", Command)))
async def addf(client,message):
	"""Adds current chat to connected federations."""
	if not DB_AVAILABLE:
		await message.edit("Your database is not avaiable!")
		return

	text = (message.text).split(None,1)
	if len(text) < 2:
		await message.edit("**Pass a name in order connect to this group!**")
		return
	fed_name = text[1]
	if not sql.add_flist(message.chat.id, fed_name):
		await message.edit("**This group is already connected to federations list.**")
		return

	await message.edit("**Added this group to federations list!**")

@app.on_message(filters.me & (filters.command("delf", Command)))
async def delf(client,message):
	"""Removes current chat from connected federations."""
	if not DB_AVAILABLE:
		await message.edit("Your database is not avaiable!")
		return

	del_flist(message.chat.id)
	await message.edit("**Removed this group from federations list!**")

@app.on_message(filters.me & (filters.command("listf", Command)))
async def listf(client,message):
	"""List all connected federations."""
	if not DB_AVAILABLE:
		await message.edit("Your database is not avaiable!")
		return

	if len((fed_list := sql.get_flist())) == 0:
		await message.edit("**You haven't connected to any federations yet!**")
		return 

	msg = "**Connected federations:**\n\n"

	for i in fed_list:
		msg += "• " + str(i.fed_name) + "\n"

	await message.edit(msg)

@app.on_message(filters.me & (filters.command("clearf", Command)))
async def delf(client,message):
	"""Removes all chats from connected federations."""
	if not DB_AVAILABLE:
		await message.edit("Your database is not avaiable!")
		return

	sql.del_flist_all()
	await message.edit("**Disconnected from all connected federations!**")
