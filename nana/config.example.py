# Buat file config.py baru dalam dir dan impor yang sama, kemudian perpanjang kelas ini.
class Config(object):
	LOGGER = True
	# Must be filled!
	# Register here: https://my.telegram.org/apps
	api_id = 1234  # Your API_ID
	api_hash = "token"  # Your API_HASH
	DB_URI = "token"  # Your database URL

	# Version
	lang_code = "en"  # Your language code
	device_model = "PC"  # Device model
	system_version = "Linux"  # OS system type

	# Use real bot for Assistant
	# Pass False if you dont want
	ASSISTANT_BOT = True
	ASSISTANT_BOT_TOKEN = "token"
	NANA_IMG = "token"
	# Required for some features
	# Insert int id, Add someone so they can access your assistant, leave it blank if you dont want!
	AdminSettings = []
	# Insert command prefix, if you insert "!" then you can do !ping
	Command = ["!", "."]
	# WORKER must be int (number)
	NANA_WORKER = 8
	ASSISTANT_WORKER = 2
	# If True, send notification to user if Official branch has new update after running bot
	REMINDER_UPDATE = True

	# APIs token
	thumbnail_API = "token"  # Register free here: https://thumbnail.ws/
	screenshotlayer_API = "token"  # Register free here: https://screenshotlayer.com/
	gdrive_credentials = "token" # JSON output
	sw_api = "token" # Read docs in docs.spamwat.ch
	bitly_token = "token"  # register here : bitly.com
	lydia_api = "token" #get from https://coffeehouse.intellivoid.net
	remove_bg_api = "token" # Get from https://remove.bg
	HEROKU_API = "token"  # if you're using heroku this field must filled, get from here : https://dashboard.heroku.com/account
	IBM_WATSON_CRED_URL = "token"
	IBM_WATSON_CRED_PASSWORD = "token"
	time_country = '' #timezone list is in the link: https://telegra.ph/Time-Zone-list-for-Nana-Remix-07-21
	# Load or no load plugins
	# userbot
	USERBOT_LOAD = [] # Load modules you want only for user, Leave Blank if you want to use All
	USERBOT_NOLOAD = [] # Unload modules you do not like for user, Leave Blank if you want to use All
	# manager bot
	ASSISTANT_LOAD = [] # Load modules you want only for assistant, Leave Blank if you want to use All
	ASSISTANT_NOLOAD = [] # Load modules you want only for asisstant, Leave Blank if you want to use All

	# Fill this if you want to login using session code, else leave it blank
	USERBOT_SESSION = "token" # Your User session goes here
	ASSISTANT_SESSION = "token" # Your Bot session goes here
	# Pass True if you want to use test mode
	TEST_MODE = False


class Production(Config):
	LOGGER = False


class Development(Config):
	TEST_DEVELOP = None
	LOGGER = False
	TERMUX_USER = False # Make it True if you are a Termux User
	PM_PERMIT = False
