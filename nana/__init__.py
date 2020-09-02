"""
The initial start of Nana-Remix
"""
import logging
import os
import sys
import time
from inspect import getfullargspec

from .startup.var import get_var

from pydrive.auth import GoogleAuth
from pyrogram import Client, errors
from pyrogram.types import Message
from sqlalchemy import create_engine, exc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

StartTime = time.time()



TEST_DEVELOP = bool(get_var('TEST_DEVELOP', False))


if TEST_DEVELOP:
    logging.warning("Testing mode activated!")
    log = logging.getLogger()

# if version < 3.6, stop bot.
if sys.version_info[0] < 3 or sys.version_info[1] < 6:
    logging.error("You MUST have a python version of at least 3.6! Multiple features depend on this. Bot quitting.")
    quit(1)

USERBOT_VERSION = "2.1"
ASSISTANT_VERSION = "2.1"

OFFICIAL_BRANCH = ('master')
REPOSITORY = "https://github.com/pokurt/Nana-Remix.git"
RANDOM_STICKERS = ["CAADAgAD6EoAAuCjggf4LTFlHEcvNAI", "CAADAgADf1AAAuCjggfqE-GQnopqyAI",
                   "CAADAgADaV0AAuCjggfi51NV8GUiRwI"]

BOT_SESSION = "nana/session/ManageBot"
APP_SESSION = "nana/session/Nana"


# Logger
logger = get_var('LOGGER', True)
# Version
lang_code = get_var('lang_code', "en")
device_model = get_var('device_model', "PC")
system_version = get_var('system_version', "Linux")
time_country = get_var("time_country", None)

# Must be filled
api_id = get_var('api_id', None)
api_hash = get_var('api_hash', None)

# Session
USERBOT_SESSION = get_var('USERBOT_SESSION', None)
ASSISTANT_SESSION = get_var('ASSISTANT_SESSION', None)

# From config
Command = get_var("Command", "!")
NANA_WORKER = int(get_var('NANA_WORKER', 8))
ASSISTANT_WORKER = int(get_var('ASSISTANT_WORKER', 2))

try:
    TEST_DEVELOP = bool(get_var('TEST_DEVELOP', False))
    if TEST_DEVELOP:
        BOT_SESSION = get_var('BOT_SESSION', None)
        APP_SESSION = get_var('APP_SESSION', None)
    else:
        raise AttributeError
except AttributeError:
    pass

# APIs
thumbnail_API = get_var('thumbnail_API', None)
screenshotlayer_API = get_var('screenshotlayer_API', None)
bitly_token = [get_var('bitly_token', None)]
gdrive_credentials = get_var('gdrive_credentials', None)
lydia_api = get_var('lydia_api', None)
remove_bg_api = get_var('remove_bg_api', None)
sw_api = get_var('sw_api', None)
HEROKU_API = get_var('HEROKU_API', None)
IBM_WATSON_CRED_URL = get_var('IBM_WATSON_CRED_URL', None)
IBM_WATSON_CRED_PASSWORD = get_var('IBM_WATSON_CRED_PASSWORD', None)
# LOADER
USERBOT_LOAD = get_var("USERBOT_LOAD", "")
USERBOT_NOLOAD = get_var("USERBOT_NOLOAD", "")
ASSISTANT_LOAD = get_var("ASSISTANT_LOAD", "")
ASSISTANT_NOLOAD = get_var("ASSISTANT_NOLOAD", "")

DB_URI = get_var('DB_URI', "postgres://username:password@localhost:5432/database")
ASSISTANT_BOT_TOKEN = get_var('ASSISTANT_BOT_TOKEN', None)
AdminSettings = [int(x) for x in get_var("AdminSettings", "").split()]
REMINDER_UPDATE = bool(get_var('REMINDER_UPDATE', True))
TEST_MODE = bool(get_var('TEST_MODE', False))
TERMUX_USER = get_var('TERMUX_USER', False)
NANA_IMG = get_var('NANA_IMG', False)
PM_PERMIT = get_var('PM_PERMIT', False)
OwnerName = ""
app_version = "💝 Nana v{}".format(USERBOT_VERSION)
BotUsername = ""
BotID = 0
# Required for some features
# Set temp var for load later
Owner = 0
BotName = ""
OwnerUsername = ""

if os.path.exists("nana/logs/error.log"):
    f = open("nana/logs/error.log", "w")
    f.write("PEAK OF THE LOGS FILE")
LOG_FORMAT = "[%(asctime)s.%(msecs)03d] %(filename)s:%(lineno)s %(levelname)s: %(message)s"
logging.basicConfig(level=logging.ERROR,
                    format=LOG_FORMAT,
                    datefmt='%m-%d %H:%M',
                    filename='nana/logs/error.log',
                    filemode='w')
console = logging.StreamHandler()
console.setLevel(logging.ERROR)
formatter = logging.Formatter(LOG_FORMAT)
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

log = logging.getLogger()

if USERBOT_SESSION and ASSISTANT_SESSION:
    BOT_SESSION = ASSISTANT_SESSION
    APP_SESSION = USERBOT_SESSION

gauth = GoogleAuth()

DB_AVAILABLE = False
BOTINLINE_AVAIABLE = False


# Postgresql
def mulaisql() -> scoped_session:
    global DB_AVAILABLE
    engine = create_engine(DB_URI, client_encoding="utf8")
    BASE.metadata.bind = engine
    try:
        BASE.metadata.create_all(engine)
    except exc.OperationalError:
        DB_AVAILABLE = False
        return False
    DB_AVAILABLE = True
    return scoped_session(sessionmaker(bind=engine, autoflush=False))


async def get_bot_inline(bot):
    global BOTINLINE_AVAIABLE
    if setbot:
        try:
            await app.get_inline_bot_results("@{}".format(bot.username), "test")
            BOTINLINE_AVAIABLE = True
        except errors.exceptions.bad_request_400.BotInlineDisabled:
            BOTINLINE_AVAIABLE = False


async def get_self():
    global Owner, OwnerName, OwnerUsername, AdminSettings
    getself = await app.get_me()
    Owner = getself.id
    if getself.last_name:
        OwnerName = getself.first_name + " " + getself.last_name
    else:
        OwnerName = getself.first_name
    OwnerUsername = getself.username
    if Owner not in AdminSettings:
        AdminSettings.append(Owner)


async def get_bot():
    global BotID, BotName, BotUsername
    getbot = await setbot.get_me()
    BotID = getbot.id
    BotName = getbot.first_name
    BotUsername = getbot.username


BASE = declarative_base()
SESSION = mulaisql()

setbot = Client(BOT_SESSION, api_id=api_id, api_hash=api_hash, bot_token=ASSISTANT_BOT_TOKEN, workers=ASSISTANT_WORKER,
                test_mode=TEST_MODE)

app = Client(APP_SESSION, api_id=api_id, api_hash=api_hash, app_version=app_version, device_model=device_model,
             system_version=system_version, lang_code=lang_code, workers=NANA_WORKER, test_mode=TEST_MODE)


async def edrep(msg: Message, **kwargs):
    func = msg.edit_text if msg.from_user.is_self else msg.reply
    spec = getfullargspec(func.__wrapped__).args
    await func(**{k: v for k, v in kwargs.items() if k in spec})