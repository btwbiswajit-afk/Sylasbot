"""
╔══════════════════════════════════════════════╗
║  𝑆ʏ𝐿ᴀs 𝑮ᴏᴅ 𝐏ʏ                      ║
║    𝐆ᴏɴɴᴀ 𝐅ᴜᴄᴋ 𝐘ᴏᴜʀ 𝐀Lʟ ᴛᴏᴏʟs        ║
╚══════════════════════════════════════════════╝
"""

import asyncio
import os
import sys
import tempfile
import time
import random
import re
import io
import json
import yt_dlp
from aiohttp import web
from gtts import gTTS
import edge_tts
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.channels import (
    InviteToChannelRequest,
    EditAdminRequest,
    EditTitleRequest
)
from telethon.tl.functions.messages import (
    AddChatUserRequest,
    DeleteMessagesRequest
)
from telethon.tl.types import ChatAdminRights
from telethon.errors import (
    UserPrivacyRestrictedError,
    PeerFloodError,
    SessionPasswordNeededError
)
from telegram import Update, Bot, ChatPermissions
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ChatMemberHandler,
    filters,
    ContextTypes
)
from telegram.error import (
    TelegramError,
    Conflict as TelegramConflict,
    RetryAfter,
    TimedOut,
    NetworkError
)
from telegram.request import HTTPXRequest

# ═══════════════ 𝐌𝐈𝐗 𝐅𝐎𝐍𝐓 ═══════════════
def mf(text):
    normal_lower = "abcdefghijklmnopqrstuvwxyz"
    mix_lower    = "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ"
    normal_upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    mix_upper    = "𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙"
    result = ""
    for char in text:
        if char in normal_lower:
            result += mix_lower[normal_lower.index(char)]
        elif char in normal_upper:
            result += mix_upper[normal_upper.index(char)]
        else:
            result += char
    return result

# ═══════════════ 𝐄𝐍𝐕𝐈𝐑𝐎𝐍𝐌𝐄𝐍𝐓 𝐕𝐀𝐑𝐈𝐀𝐁𝐋𝐄𝐒 ═══════════════
def get_env(name, default=""):
    return os.getenv(name, default).strip()

# ═══════════════ 𝐂𝐎𝐍𝐅𝐈𝐆 ═══════════════
API_ID = int(get_env("API_ID", "32070897"))
API_HASH = get_env("API_HASH", "445b591a8ce0d236a81f47b68a8f2a1d")
OWNER_ID = int(get_env("OWNER_ID", "8663186943"))

BOT_TOKENS = []
for i in range(1, 11):
    token = get_env(f"BOT_TOKEN_{i}")
    if token:
        BOT_TOKENS.append(token)

if not BOT_TOKENS:
    BOT_TOKENS = [
        "8368771798:AAEgjAIma4KMRbrRJV240LuaS23NC9yUa6g",
        "8715692930:AAEi2_ZDjwHuU82UyWFLTJF-WOiuVCas1pI",
        "8464120565:AAECYne22xObdbL3wCfP1dwAkSZY4pBbcuc",
        "8825778408:AAE3YixLczfAw9bpvuzJUkLs5ikpJHt5IiU",
        "8898121503:AAHYiN__hHnhrOeXAhZrZXWndRdEzjPHeKg",
        "8884160787:AAEy1ScQP_8OhLlpjEoS6hJ6CdZaOnFL7TU",
        "8902827296:AAFsZGqvwGqe9GlbpdF8_ikyIiwadNgzvHY",
        "8837965287:AAH_m3AASDgiJP25fHvjS0vDv-RIWAGMq64",
        "8391400841:AAGAA83qXYtihGkuxEWOcEsVdyBWPxUZWL8",
        "8696798121:AAHBmK2hwMdTngzQhp1AS26m6IceLGPTF1s",
    ]

ADMIN_IDS = [OWNER_ID]
AUTO_DEL = 5
MAX_AUDIO_MB = 50
SESSION_FILE = "session_string.txt"
NC_DELAY = 2

START_REPLY = mf("Bhag Bsdke Garib Phele Sylas Baap Se Sudo Lee")
UNAUTH = mf("Bhag Bsdke Garib Phele Sylas Baap Se Sudo Lee")

# ═══════════════ 𝐏𝐑𝐎𝐗𝐘 𝐒𝐘𝐒𝐓𝐄𝐌 ═══════════════
PROXY_LIST = []
if os.path.exists("proxies.txt"):
    with open("proxies.txt") as f:
        PROXY_LIST = [line.strip() for line in f if line.strip()]

def get_proxy(bot_num):
    if PROXY_LIST:
        return PROXY_LIST[(bot_num - 1) % len(PROXY_LIST)]
    return None

# ═══════════════ 𝐆𝐋𝐎𝐁𝐀𝐋 𝐒𝐓𝐀𝐓𝐒 ═══════════════
GLOBAL_STATS = {
    "messages_sent": 0,
    "name_changes": 0,
    "replies_sent": 0,
    "rspam_sent": 0,
    "start_time": time.time(),
}

# ═══════════════ 𝐁𝐎𝐓 𝐈𝐍𝐒𝐓𝐀𝐍𝐂𝐄 𝐂𝐋𝐀𝐒𝐒 ═══════════════
class BotInstance:
    def __init__(self, bot_number):
        self.bot_number = bot_number
        self.proxy = get_proxy(bot_number)
        
    def __repr__(self):
        return f"BotInstance({self.bot_number})"

# ═══════════════ 𝐓𝐀𝐒𝐊 𝐃𝐈𝐂𝐓𝐒 ═══════════════
NC_TASKS = {}
SPAM_TASKS = {}
RSPAM_TASKS = {}
RSPAM_TARGETS = {}
REPLY_TASKS = {}
RR_TASKS = {}
PICSPAM_TASKS = {}
PFP_TASKS = {}
EMOJI_TASKS = {}
TTSSPAM_TASKS = {}
PENDING_REPLIES = {}
PENDING_RR = {}
RR_TARGETS = {}
CHAT_DELAYS = {}
CHAT_THREADS = {}
PICSPAM_FILE_IDS = {}
REACT_CHATS = {}
REACT_EMOJI = {}
ALL_BOT_APPS = []

# ═══════════════ 𝐇𝐎𝐒𝐓𝐈𝐍𝐆 𝐒𝐘𝐒𝐓𝐄𝐌 ═══════════════
HOSTED_BOTS_FILE = "hosted_bots.json"
HOSTED_BOTS = {}
HOSTED_APPS = []
HOSTED_BOT_COUNTER = 0

def load_hosted_bots():
    global HOSTED_BOTS
    if os.path.exists(HOSTED_BOTS_FILE):
        try:
            with open(HOSTED_BOTS_FILE) as f:
                HOSTED_BOTS = json.load(f)
        except:
            HOSTED_BOTS = {}
    else:
        HOSTED_BOTS = {}

def save_hosted_bots():
    try:
        with open(HOSTED_BOTS_FILE, "w") as f:
            json.dump(HOSTED_BOTS, f)
    except:
        pass

load_hosted_bots()

# ═══════════════ 𝐌𝐄𝐒𝐒𝐀𝐆𝐄𝐒 ═══════════════
NC_TIME_EMOJIS = ["⭐","🌟","💫","✨","⚡","🔥","💎","👑","🎯","💠","🔱","🪐"]
NC_TIME_END = ["RΛɴᴅʏᴋᴇ LΛᴅҡᴇ "]

NC2_EMOJIS = ["❤️","🩷","💖","💜","🖤","💛","💚","💙","🧡","💝","💗","💓"]
NC2_END = [
" ᴋᴀᴍᴢᴏʀ",
" ʙᴄ",
" ᴄᴜᴅ",
" ᴛᴍʀ",
" ʀɴᴅ",
" ʀᴏᴏ",
" ʟᴏᴅᴀ ʟᴇ",
" ᴄᴠʀ ᴋʀ",
" ʀɴᴅ",
" ᴛᴍᴋʟ",
" 𝑺ʏ𝑳ᴀs ꜱᴇ ᴄʜᴜᴅᴏ",
" ʙʜᴀᴅᴠᴇ",
" ʜɪᴢᴅᴇ",
" ᴛᴇʀɪ ʙʜɴ ʀɴᴅ",
" ᴘʏ ꜱɪᴋʜᴀᴜ",
" ᴄᴜᴅᴀᴋᴀᴀᴅ",
" ᴘʏ ꜱᴇ ᴄʜᴜᴅ",
" ᴘʏ ᴅᴇᴋʜ",
" ᴘʏ ʟᴀɢᴀɴᴀ ꜱɪᴋʜᴀᴜ",
" ᴋᴜᴛᴛɪ",
" ᴘʏ ꜱᴇ ᴄʜᴜᴅ",
" ᴄʜᴜꜱꜱᴀ ᴍᴀʀ",
" ᴋɪᴅᴇ",
" ᴘʏ ɴᴄ ʜᴀɪ ʏᴇ",
" ʀᴏᴏ",
" ᴛᴇʀɪ ʙʜɴ ʀɴᴅ",
" ɢᴜʟᴀᴍ",
" ʙɪᴛᴄʜ",
" ʀᴀɴᴅɪ",
" ɢᴀɴᴅ ᴍʀᴀ",
" ꜱᴘᴇᴇᴅ ʟᴀ",
" ᴄʜᴜᴅᴀɪ ᴋᴇ ʙᴀᴋʀᴇ",
" ɢᴀɴᴅᴜ",
" ʟᴜɴᴅ ᴄʜᴜᴅ"
]

NC3_END = [
    "Gᴜʟᴀᴍɪ ᴋʀ ",
    "Tᴇʀɪ Mᴀᴀ Cʜᴜᴅɪ ",
    "Sᴀʟᴀᴍ Tʜᴏᴋ ",
    "Cʜɪɴᴀᴀʀ ",
    "Mᴀᴢᴅᴏᴏʀ ",
    "Hᴀᴡᴀʙᴀᴢᴢ ",
    "Sʏʟᴀs अब्बू  ʙᴏʟ",
    "Tᴍᴋʟ ",
    "ᴋᴀᴍᴢᴏʀ Kᴜᴛɪʏᴀ ",
    "Bʜᴇᴇᴋ Mᴀɴɢ ",
    "RɴᴅɪMᴏɴ ",
    "Cʜᴜᴅᴀɪ Kɪᴅᴅᴇ ",
    "Gʜᴀᴛɪʏᴀ Bᴇᴛᴀ ",
    "Tᴇʀᴀ Bᴀᴀᴘ Sʏʟᴀs ",
    "GAɴᴅ Mᴀʀᴀ ᴍᴜʟʟᴇ ",
    "Cʜᴜᴅᴇɢɪ TᴇʀɪMA ",
    "BɪᴛCʜ ",
    "HɪᴊᴅᴜSᴏɴ ",
    "Nᴀʟɪ Sᴀғ Kᴀʀ ᴊAᴋᴇ ",
    "GʜɪNᴏɴɪ Rɴᴅ ",
    "Cʜᴏᴛɪ Jᴀᴀᴛ ",
    "TᴇRɪ Mᴀ Cʜɪɴᴀᴀʀ ",
    "Hɪᴊᴀʙ PᴇʜᴇN ",
    "Tᴍᴋᴄ Mᴀɪ Kᴏʏʟᴀ ",
]

# /sylasnc — Pookie Style
SYLASNC_EMOJIS = ["🎀","💅","✨","🌟","💋","🫦","👅","💖","🩷","💜","🖤","🧡","💝","💗","💓","💞","🌸","🌺","💐","🦋"]
SYLASNC_END = ["𝐓ᴍᴋᴄ 𝐑ᴜɴᴅʏ 𝐊ᴇ"]
SYLASNC_MSGS = [
    "{n} > LᴜɴɴCʜᴜssᴇʀ Bɪᴛᴄʜs ⸻➤({e})",
    "{n} > WᴏʀsHɪᴘ Us AɴD Sᴀʏ ᴏᴏ LᴏRᴅ Gɪᴠᴇ Mᴇ SᴏᴍE CʜᴜDᴀɪ ⸻➤({e})",
    "{n} > Sᴀʏ FᴜᴄK Mᴇʜʜ ⸻➤({e})",
    "{n} > TᴍᴋᴄKɪᴅᴅᴏ ⸻➤({e})",
    "{n} > TʙᴋC ⸻➤({e})",
    "{n} > GʜɪNᴏɴɪ RɴᴅY Kᴇ Bᴄᴄʜᴇ ⸻➤({e})",
    "{n} > HɪᴢRᴜBᴏɪ ⸻➤({e})",
    "{n} > TʀʏᴍAᴋɪ Pᴜssʏ P sᴛᴏNᴇ PᴇʟᴛɪNɢ Kʀᴜ? ⸻➤({e})",
    "{n} > Lᴜɴ Kʜᴀ PᴏᴋEᴍᴏN ⸻➤({e})",
    "{n} > TʀʏMᴀᴀ ᴄʜᴜD CʜᴜD Kᴇ sɪᴄK Hɢʏɪ ⸻➤({e})",
    "{n} > Sᴘᴇᴄs PʜN ᴋE TᴍᴋC ᴘ AᴀJᴊ RᴇʜPᴀᴛ Lᴀɴɢᴇɴɢᴇ ⸻➤({e})",
    "{n} > TᴇRɪ MᴀA Kᴏ ᴘʜUɴsɪ PʜᴏD BᴀBᴀ Kᴇ PᴀsS ᴄʜᴏRᴅ Nɪ ᴘᴀDᴇɢɪ ⸻➤({e})",
    "{n} > CʜᴜᴅEɢɪ Tʀʏᴍᴀ ⸻➤({e})",
    "{n} > HɪᴊAʙ MᴄʜᴜDʟᴇ ⸻➤({e})",
    "{n} > Sᴀʏ 𝘚ꪗꪶꪖ𝘴 DᴀᴅDʏ ⸻➤({e})",
    "{n} > GᴀɴD Mʀᴡᴀ Bsᴅᴋ ⸻➤({e})",
    "{n} > TʀɪMᴀ CʜᴜDᴋᴅ ⸻➤({e})",
]

# /tridentnc — Curly Style
TRIDENT_EMOJIS = [
        r"{target} ƬEƦƖ Ɱƛ ƘƠ ƇӇƠƊƲƝ𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤ 𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤(💔)",
        r"{target} ƬEƦƖ Ɱƛ ƘƠ ƇӇƠƊƲƝ𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤ 𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤(❤️)",
        r"{target} ƬEƦƖ Ɱƛ ƘƠ ƇӇƠƊƲƝ𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤ 𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤(🧡)",
        r"{target} ƬEƦƖ Ɱƛ ƘƠ ƇӇƠƊƲƝ𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤ 𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤(💛)",
        r"{target} ƬEƦƖ Ɱƛ ƘƠ ƇӇƠƊƲƝ𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤ 𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤(💚)",
        r"{target} ƬEƦƖ Ɱƛ ƘƠ ƇӇƠƊƲƝ𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤ 𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤(🩶)",
        r"{target} ƬEƦƖ Ɱƛ ƘƠ ƇӇƠƊƲƝ𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤ 𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤(🤎)",
        r"{target} ƬEƦƖ Ɱƛ ƘƠ ƇӇƠƊƲƝ𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤ 𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤(💜)",
        r"{target} ƬEƦƖ Ɱƛ ƘƠ ƇӇƠƊƲƝ𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤ 𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤(💙)",
        r"{target} ƬEƦƖ Ɱƛ ƘƠ ƇӇƠƊƲƝ𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤ 𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤𒀱ꪳ🩵𒀱ꪳ💛𒀱ꪳ💚𒀱ꪳ❤(🩵)"
    ]
TRIDENT_END = [
        r"{target} 𝘔𝘈𝘋𝘈𝘙𝘊𝘏𝘖𝘋 𝘖𝘠𝘌𝘌𝘌𝘌𝘌𝘌.....,🥶🤍💢᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄༺═──────────────═༻☟☜♻𓂃𓂃𓂃♻᳄᳄᳄᳄᳄᳄᳄༺═────(🌀)",
        r"{target} 𝘔𝘈𝘋𝘈𝘙𝘊𝘏𝘖𝘋 𝘖𝘠𝘌𝘌𝘌𝘌𝘌𝘌.....,🥶🤍💢᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄༺═──────────────═༻☟☜♻𓂃𓂃𓂃♻᳄᳄᳄᳄᳄᳄᳄༺═────(🔥)",
        r"{target} 𝘔𝘈𝘋𝘈𝘙𝘊𝘏𝘖𝘋 𝘖𝘠𝘌𝘌𝘌𝘌𝘌𝘌.....,🥶🤍💢᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄༺═──────────────═༻☟☜♻𓂃𓂃𓂃♻᳄᳄᳄᳄᳄᳄᳄༺═────(💀)",
        r"{target} 𝘔𝘈𝘋𝘈𝘙𝘊𝘏𝘖𝘋 𝘖𝘠𝘌𝘌𝘌𝘌𝘌𝘌.....,🥶🤍💢᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄༺═──────────────═༻☟☜♻𓂃𓂃𓂃♻᳄᳄᳄᳄᳄᳄᳄༺═────(⚡)",
        r"{target} 𝘔𝘈𝘋𝘈𝘙𝘊𝘏𝘖𝘋 𝘖𝘠𝘌𝘌𝘌𝘌𝘌𝘌.....,🥶🤍💢᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄༺═──────────────═༻☟☜♻𓂃𓂃𓂃♻᳄᳄᳄᳄᳄᳄᳄༺═────(😈)",
        r"{target} 𝘔𝘈𝘋𝘈𝘙𝘊𝘏𝘖𝘋 𝘖𝘠𝘌𝘌𝘌𝘌𝘌𝘌.....,🥶🤍💢᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄༺═──────────────═༻☟☜♻𓂃𓂃𓂃♻᳄᳄᳄᳄᳄᳄᳄༺═────(☠️)",
        r"{target} 𝘔𝘈𝘋𝘈𝘙𝘊𝘏𝘖𝘋 𝘖𝘠𝘌𝘌𝘌𝘌𝘌𝘌.....,🥶🤍💢᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄༺═──────────────═༻☟☜♻𓂃𓂃𓂃♻᳄᳄᳄᳄᳄᳄᳄༺═────(🌪️)",
        r"{target} 𝘔𝘈𝘋𝘈𝘙𝘊𝘏𝘖𝘋 𝘖𝘠𝘌𝘌𝘌𝘌𝘌𝘌.....,🥶🤍💢᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄༺═──────────────═༻☟☜♻𓂃𓂃𓂃♻᳄᳄᳄᳄᳄᳄᳄༺═────(👑)",
        r"{target} 𝘔𝘈𝘋𝘈𝘙𝘊𝘏𝘖𝘋 𝘖𝘠𝘌𝘌𝘌𝘌𝘌𝘌.....,🥶🤍💢᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄༺═──────────────═༻☟☜♻𓂃𓂃𓂃♻᳄᳄᳄᳄᳄᳄᳄༺═────(💥)",
        r"{target} 𝘔𝘈𝘋𝘈𝘙𝘊𝘏𝘖𝘋 𝘖𝘠𝘌𝘌𝘌𝘌𝘌𝘌.....,🥶🤍💢᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄༺═──────────────═༻☟☜♻𓂃𓂃𓂃♻᳄᳄᳄᳄᳄᳄᳄༺═────(🚨)"
    ]
TRIDENT_MSGS = [
        r"˚⊱━━😛━━⊰˚{target} chote bhag rndice 𒐫𒐫𒐫𒐫𒐫𒐫𒐫✨✨✨𒐫✨✨✨𒐫✨✨✨𒐫𒐫✨✨𒐫✨✨✨𒐫✨✨𒐫𒐫✨✨✨𒐫𒐫𒐫𒐫𒐫𒐫𒐫✨✨𒐫𒐫𒐫✨𒐫✨✨𒐫𒐫✨✨𒐫✨✨𒐫𒐫𒐫✨🎀✨",
        r"˚⊱━━🔥━━⊰˚{target} chote bhag rndice 𒐫𒐫𒐫𒐫𒐫𒐫𒐫✨✨✨𒐫✨✨✨𒐫✨✨✨𒐫𒐫✨✨𒐫✨✨✨𒐫✨✨𒐫𒐫✨✨✨𒐫𒐫𒐫𒐫𒐫𒐫𒐫✨✨𒐫𒐫𒐫✨𒐫✨✨𒐫𒐫✨✨𒐫✨✨𒐫𒐫𒐫✨🎀✨",
        r"˚⊱━━💀━━⊰˚{target} chote bhag rndice 𒐫𒐫𒐫𒐫𒐫𒐫𒐫✨✨✨𒐫✨✨✨𒐫✨✨✨𒐫𒐫✨✨𒐫✨✨✨𒐫✨✨𒐫𒐫✨✨✨𒐫𒐫𒐫𒐫𒐫𒐫𒐫✨✨𒐫𒐫𒐫✨𒐫✨✨𒐫𒐫✨✨𒐫✨✨𒐫𒐫𒐫✨🎀✨",
        r"˚⊱━━⚡━━⊰˚{target} chote bhag rndice 𒐫𒐫𒐫𒐫𒐫𒐫𒐫✨✨✨𒐫✨✨✨𒐫✨✨✨𒐫𒐫✨✨𒐫✨✨✨𒐫✨✨𒐫𒐫✨✨✨𒐫𒐫𒐫𒐫𒐫𒐫𒐫✨✨𒐫𒐫𒐫✨𒐫✨✨𒐫𒐫✨✨𒐫✨✨𒐫𒐫𒐫✨🎀✨",
        r"˚⊱━━😈━━⊰˚{target} chote bhag rndice 𒐫𒐫𒐫𒐫𒐫𒐫𒐫✨✨✨𒐫✨✨✨𒐫✨✨✨𒐫𒐫✨✨𒐫✨✨✨𒐫✨✨𒐫𒐫✨✨✨𒐫𒐫𒐫𒐫𒐫𒐫𒐫✨✨𒐫𒐫𒐫✨𒐫✨✨𒐫𒐫✨✨𒐫✨✨𒐫𒐫𒐫✨🎀✨",
        r"˚⊱━━☠️━━⊰˚{target} chote bhag rndice 𒐫𒐫𒐫𒐫𒐫𒐫𒐫✨✨✨𒐫✨✨✨𒐫✨✨✨𒐫𒐫✨✨𒐫✨✨✨𒐫✨✨𒐫𒐫✨✨✨𒐫𒐫𒐫𒐫𒐫𒐫𒐫✨✨𒐫𒐫𒐫✨𒐫✨✨𒐫𒐫✨✨𒐫✨✨𒐫𒐫𒐫✨🎀✨",
        r"˚⊱━━🌪️━━⊰˚{target} chote bhag rndice 𒐫𒐫𒐫𒐫𒐫𒐫𒐫✨✨✨𒐫✨✨✨𒐫✨✨✨𒐫𒐫✨✨𒐫✨✨✨𒐫✨✨𒐫𒐫✨✨✨𒐫𒐫𒐫𒐫𒐫𒐫𒐫✨✨𒐫𒐫𒐫✨𒐫✨✨𒐫𒐫✨✨𒐫✨✨𒐫𒐫𒐫✨🎀✨",
        r"˚⊱━━👑━━⊰˚{target} chote bhag rndice 𒐫𒐫𒐫𒐫𒐫𒐫𒐫✨✨✨𒐫✨✨✨𒐫✨✨✨𒐫𒐫✨✨𒐫✨✨✨𒐫✨✨𒐫𒐫✨✨✨𒐫𒐫𒐫𒐫𒐫𒐫𒐫✨✨𒐫𒐫𒐫✨𒐫✨✨𒐫𒐫✨✨𒐫✨✨𒐫𒐫𒐫✨🎀✨",
        r"˚⊱━━💥━━⊰˚{target} chote bhag rndice 𒐫𒐫𒐫𒐫𒐫𒐫𒐫✨✨✨𒐫✨✨✨𒐫✨✨✨𒐫𒐫✨✨𒐫✨✨✨𒐫✨✨𒐫𒐫✨✨✨𒐫𒐫𒐫𒐫𒐫𒐫𒐫✨✨𒐫𒐫𒐫✨𒐫✨✨𒐫𒐫✨✨𒐫✨✨𒐫𒐫𒐫✨🎀✨",
        r"˚⊱━━🚨━━⊰˚{target} chote bhag rndice 𒐫𒐫𒐫𒐫𒐫𒐫𒐫✨✨✨𒐫✨✨✨𒐫✨✨✨𒐫𒐫✨✨𒐫✨✨✨𒐫✨✨𒐫𒐫✨✨✨𒐫𒐫𒐫𒐫𒐫𒐫𒐫✨✨𒐫𒐫𒐫✨𒐫✨✨𒐫𒐫✨✨𒐫✨✨𒐫𒐫𒐫✨🎀✨"
    ]

# /sync — Big Style
SYNC_SYMBOLS = ["𒈙"]
SYNC_EMOJIS = ["☢️","🩷","🔥","🦈","👾","❄️","💠","🀄","🧃","☀️","🫧","🥁","💀","🖤","🌟"]
SYNC_END = ["ᑕʜꪊD"]

# /sylasnc2 — Heart Style
SYLASNC2_HEARTS = ["❤️","❤️‍🩹","💕","💞","💓","💗","💖","💘","💝","🩷","♥️","❣️","💟","🫶","🤍"]

def gen_sylasnc2(n):
    heart = random.choice(SYLASNC2_HEARTS)
    return f"{n} 𝑺𝒀𝑳𝑨𝑺<>𝑬𝑵𝑻𝑬𝑹𝑺{heart}"

# ═══════════════ 𝐒𝐏𝐀𝐌 𝐌𝐄𝐒𝐒𝐀𝐆𝐄𝐒 ═══════════════
SPAM_MSG = [
        r"✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Kᴀʟᴡɪ 「🎀」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Kᴀʟᴡɪ 「🤍」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Kᴀʟᴡɪ 「🎀」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Kᴀʟᴡɪ 「🤍」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Kᴀʟᴡɪ 「🎀」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Kᴀʟᴡɪ 「🤍」",
        r"✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Bᴀᴜɴɪ 「✨」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Bᴀᴜɴɪ 「🩷」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Bᴀᴜɴɪ 「✨」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Bᴀᴜɴɪ 「🩷」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Bᴀᴜɴɪ 「✨」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Bᴀᴜɴɪ 「🩷」",
        r"✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Hᴀᴋʟɪ 「💫」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Hᴀᴋʟɪ 「🩵」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Hᴀᴋʟɪ 「💫」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Hᴀᴋʟɪ 「🩵」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Hᴀᴋʟɪ 「💫」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Hᴀᴋʟɪ 「🩵」",
        r"✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Lᴀɴɢᴅɪ 「🌙」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Lᴀɴɢᴅɪ 「🖤」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Lᴀɴɢᴅɪ 「🌙」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Lᴀɴɢᴅɪ 「🖤」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Lᴀɴɢᴅɪ 「🌙」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Lᴀɴɢᴅɪ 「🖤」"
    ]

REPLY_MSG = [
  "{target} Tᴇʀɪ ᴍᴀᴀ ɢᴜʟᴀᴍ ʜ ʙᴇᴛᴇ🐣",
    "{target} Cᴜᴅ Cᴜᴅ Cᴜᴅ -!🩴🔥",
    "Aʟᴏᴏ Kʜᴀᴋᴇ {target} Tᴇʀɪ Mᴀᴀ 𝑺ʏ𝑳ᴀs Kɪ Pᴇʀꜱᴏɴᴀʟ Rɴᴅʏ 👑♥️",
    "{target} Hɪᴊᴅᴇ Aᴩɴɪ Mᴀᴀ Kᴇ Jᴀɪꜱᴇ Aᴄʜᴇ Sᴇ Cʜᴜᴅ🤳🏻👋🏻",
    "{target} Tᴇʀᴇ Kʜᴀɴᴅᴀɴ Kɪ Mᴀᴀ Cʜᴏᴅᴜ🔥✨",
    "{target} Tᴜ ᴋʀᴇɢᴀ Sᴘᴀᴍ Nᴇᴡ Gᴇɴ?🔃💠",
    "{target} Tᴇʀɪ Bʜᴇɴ Kᴏ Dɪɴᴏꜱᴏᴜʀ Cʜᴏᴅᴇɢᴀ 🦖😈",
    "{target} Gᴜʟᴀᴍ Jʜᴜᴋᴊᴀ OR 𝑺ʏ𝑳ᴀs Dᴀᴅᴅʏ Kᴇ Lɴᴅ Pᴇ Jʜᴜʟᴊᴀ🖤🙊",
    "{target} Tᴇʀɪ Mᴜᴍᴍʏ Kᴏ Kᴜᴛɪʏᴀ Bᴀɴᴀ Kʀ Cʜᴏᴅᴜ🌷😭",
    "{target} Tᴇʀɪ Bᴀʜᴇɴ Kᴇ Cʜᴜᴄʜᴇ Dᴀʙᴀ Dᴜ😨♥️",
    "{target} Nᴀ Hᴀᴛʜɪ Nᴀ Gʜᴏᴅᴀ Tᴍᴋᴄ Mᴀɪ 𝑺ʏ𝑳ᴀs Dᴀᴅᴅʏ Kᴀ Lᴏᴅᴀ 💀🥵",
    " Pᴀɴɪ Pɪʏᴜɴɢᴀ Bᴏᴛᴛʟᴇ Mᴀɪ {target} Kɪ Mᴀᴀ Cʜᴏᴅᴜ Hᴏᴛᴇʟ Mᴀɪ 🥧🧑🏻‍🍳",
    "{target} Eᴠᴇʀʏᴛʜɪɴɢ Is Tᴇᴍᴘᴏʀᴀʀʏ Bᴜᴛ Tᴇʀɪ Bᴀʜᴇɴ Kɪ Cʜᴜᴅᴀɪ Is ᴘᴇʀᴍᴀɴᴇɴᴛ 🦠🦷",
    "{target} ᴋᴀʜᴀ ᴛᴀᴋ ʙʜᴀɢᴇɢᴀ Eᴋ ʀᴇʜᴘᴀᴛ ᴍ ᴛᴇʀᴀ Rᴀᴘᴇ ʜᴏᴊʏᴇɢᴀ Bʜᴇɴɢᴇ🦘🪽",
    "{target} Tᴇʀɪ Mᴀᴀ ᴘᴇsᴇ ᴋᴀᴍᴀᴛᴇ ᴋᴀᴍᴀᴛᴇ ɴᴀɴɢɪ Hᴜɪ 👩🏻‍⚕️👩🏻‍🎤",
    "{target} Tᴇʀɪ ᴍᴀᴀ ᴋᴏ Mᴇʀᴇ FᴀʀᴍHᴏᴜsᴇ P ʙʜᴇᴊᴅᴇ🥩🍏",
    "{target} Kᴜᴛɪʏᴀ Kᴇ ʙʜᴏsᴅᴇ Kɪ ᴀᴜʟᴀᴅ😈👋🏻",
    " Uɴɪᴠʀꜱᴇ Mᴀɪ Bʟᴀᴄᴋ Hᴏʟᴇ {target} Kɪ Mᴀᴀ Aᴩɴɪ Pᴀɴᴛʏ Kʜᴏʟ🕳️🔥",
    "{target} ʜɪᴊᴅᴀ ʜ ᴛᴜ ɢʀᴇᴇʙ💮🥀",
    "{target} Tᴇʀɪ Bᴀʜᴇɴ Kᴇ Cʜᴜᴛ Mᴀɪ Cʜᴀᴩᴩᴀʟ🩴🔥",
    """➞ {target} मादर चोद ⏤͟͟͞͞꙰「💀」""",
"""➞ {target} की गांड फटी ⏤͟͟͞͞꙰「🔥」""",
"""➞ {target} रंड ⏤͟͟͞͞꙰「🤣」""",
"""➞ {target} के पिता श्री  𓆩 𝑺ʏ𝑳ᴀs𓆪 ⏤͟͟͞͞꙰⏤͟͟͞͞꙰「❤️」""",
"""➞ {target} मादर चोद ⏤͟͟͞͞꙰⏤͟͟͞͞꙰「💀」""",
"""➞ {target}  TMKC KEEDE⏤͟͟͞͞꙰⏤͟͟͞͞꙰「🫶🏻」""",
"""➞ {target} BHIKARI RNDY ⏤͟͟͞͞꙰⏤͟͟͞͞꙰「😎」""",
"""➞ {target} TMKC MARU ⏤͟͟͞͞꙰⏤͟͟͞͞꙰「🤣」""",
"""➞ {target} 🇹‌🇲‌🇰‌🇨‌ ⏤͟͟͞͞꙰⏤͟͟͞͞꙰「😏」""",
"""➞ {target} 🇲‌🇨‌ ⏤͟͟͞͞꙰⏤͟͟͞͞꙰「🤤」""",
"""➞ {target} 🇷‌🇳‌🇩‌🇾‌ ⏤͟͟͞͞꙰⏤͟͟͞͞꙰「😍」""",
"""➞ {target} 🇹‌🇲‌🇰‌🇧‌ ⏤͟͟͞͞꙰⏤͟͟͞͞꙰「😈」""",
"""➞ {target} 𝟔 🇰‌ ⏤͟͟͞͞꙰⏤͟͟͞͞꙰「❤️‍🔥」""",
"""➞ {target} 𝘎𝘙𝘌𝘉 𝘉𝘏𝘐𝘒𝘈𝘙𝘐 ⏤͟͟͞͞꙰⏤͟͟͞͞꙰「💝」""",
"""➞ {target} 🅁🄰🄰🄽🄳 ⏤͟͟͞͞꙰⏤͟͟͞͞꙰「💌」""",
"""➞ {target} αpnє पिता श्री  𓆩 𓆩𓆩⃟👑⃟𓆪𓆪 𝑺ʏ𝑳ᴀs 𓆩𓆩⃟ 🔱 ⃟𓆪𓆪𓆪 𝘒𝘖 𝘛𝘌𝘙𝘐 𝘔𝘈𝘈 𝘚𝘈𝘓𝘈𝘔 𝘒𝘈𝘙𝘌𝘎𝘐?? ⏤͟͟͞͞꙰⏤͟͟͞͞꙰「💥」""",
"""➞ {target} 𝘛𝘔𝘒𝘊 𝘈𝘜𝘒𝘈𝘛??? ⏤͟͟͞͞꙰⏤͟͟͞͞꙰「💫」""",
"""➞ {target} 𝘔𝘈𝘑𝘋𝘜𝘙 𝘙𝘌𝘈𝘓 𝘓𝘐𝘍𝘌 𝘔𝘌 𝘋𝘐𝘏𝘈𝘋?? 𝘓𝘈𝘎𝘈 ⏤͟͟͞͞꙰⏤͟͟͞͞꙰「👑」""",
"""➞ {target} TEᖇI ᗰᗩKI 🄿🅄🅂🅂🄷🅈 ¢нαтυ⏤͟͟͞͞꙰⏤͟͟͞͞꙰「😝」""",
"""➞ {target} 🇹‌🇪‌🇷‌🇮‌   𝐌𝐀𝐊𝐈   𝙱𝚁𝙰 𝚃𝙸𝙶𝙷𝚃??? ⏤͟͟͞͞꙰⏤͟͟͞͞꙰「❤️‍🩹」""",
"""➞ {target} 𝗞𝗜 𝗕𝗔𝗛𝗘𝗡 𝗦𝗘𝗫𝗬 ⏤͟͟͞͞꙰⏤͟͟͞͞꙰「🤪」""",
"""➞ {target} 𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗜 𝗖𝗛𝟳𝗧 𝗠𝗔𝗥 𝗗𝗨𝗡𝗚𝗔⏤͟͟͞͞꙰⏤͟͟͞͞꙰「🤬」""",
"""➞ {target} के पिता श्री  𓆩 𝑺ʏ𝑳ᴀs?? ᴋᴏ ꜱᴀʟᴀᴍ ᴛʜᴏᴋ ᴍᴄ ⏤͟͟͞͞꙰⏤͟͟͞͞꙰「🥶」""",
"""➞ {target} 𝙰𝙿ɴ𝙴 पिता श्री  𓆩 𝑺ʏ𝑳ᴀs𓆪 ᴋᴏ ᴀᴩɴɪ ᴍᴀᴀ ᴇᴋ ʀᴀᴀᴛ ᴋᴇ ʟɪʏᴇ ᴅᴇᴅᴇ *±×  ᴊᴀᴡᴀɴ ʙᴀɴᴀ ᴅᴜɴɢᴀ ⏤͟͟͞͞꙰⏤͟͟͞͞꙰「🥵」""",
"""{target} 𝐓𝙴𝚁𝙸 𝐌𝙰𝙺𝙸 𝐂𝙷𝚄𝚃 𝐊𝙾 𝐈 𝐋𝙾𝚅𝙴 𝐘𝙾𝚄 𝐅𝚁𝙾𝙼 आपके पिता जी 𝑺ʏ𝑳ᴀs 🫶🎀""",
"""{target} 𝐓𝙴𝚁𝙸 𝐁𝙰𝙷𝙴𝙽 𝐊𝙴 𝐁𝙷𝙾𝚂𝙳𝙴 𝐌𝙰𝙸 𝐀𝙰𝙶 𝐋𝙰𝙶𝙴 🥰🤌""",
"""{target} 𝐓𝙴𝚁𝙸 𝐌𝙰𝙰 𝐊𝙰𝙷𝙰 𝐂𝙷𝚄𝚃 𝐌𝙰𝚁𝚆𝙰𝙽𝙴 𝐉𝙰𝚃𝙸 𝐇𝙰𝙸?😈👉👈""",
"""{target} 𝐊𝙸 𝐌𝙰𝙰 𝐂𝙷𝙾𝙳𝙺𝙴 𝐊𝙸𝚂𝙽𝙴 𝐏𝙰𝙸𝚂𝙰 𝐍𝙰𝙃𝙸 𝐃𝙸𝚈𝙰 𝐏𝙰𝙶𝙰𝙇 😭😂?""",
"""{target} 𝐒𝚄𝙽𝙰 𝐇𝙰𝙸 𝐓𝙴𝚁𝙸 𝐌𝙰𝙰 𝐊𝙾 𝐃𝙾𝙶𝙶𝚈 𝐒𝚃𝚈𝙻𝙴 𝐌𝙰𝙸 𝐂𝙷𝚄𝙳𝙽𝙰 𝐏𝙰𝚂𝙰𝙽𝙳 𝐇𝙰𝙸!! 𝐊𝚈𝙰 𝐘𝙴 𝐁𝙰𝙰𝚃 𝐒𝙰𝙲𝙷 𝐇𝙰𝙸??😍😝""",
"""{target} 𝐓𝙴𝚁𝙸 𝐁𝙰𝙷𝙴𝙽 𝐁𝙻𝙾𝚆 𝐉𝙾𝙱 𝐃𝙴𝚃𝙴 𝐃𝙴𝚃𝙴 𝐓𝙷𝙰𝙺 𝐆𝙰𝚈𝙸 𝐓𝙾 𝐓𝙴𝚁𝙸 𝐆𝙸𝚁𝙻𝙵𝚁𝙴𝙽𝙳 𝐁𝙻𝙾𝚆 𝐉𝙾𝙱 ??𝙴𝙶𝙸.!  𝐊𝚈𝙰 𝐘𝙴 𝐁𝙰𝙰𝚃 𝐒𝙰𝙷𝙸 𝐇𝙰𝙸?😍🥵""",
"""{target} 𝐒𝚄𝙽𝙽𝙴 𝐌𝙰𝙸 𝐀𝙰𝚈𝙰 𝐇𝙰𝙸 𝐓𝙴𝚁𝙰 𝐏𝚄𝚁𝙰 𝐊𝙷𝙰𝙽𝙳𝙰𝙽 𝐁𝙰𝙲𝙷𝙿𝙰𝙽 𝐒𝙴 𝐒𝙰𝙱 𝐋𝙾𝙶𝙾 𝐒𝙴 𝐂𝙷𝚄𝙳𝚃𝙰 𝐀𝚈𝙰 𝐇𝙰𝙸 😂😷""",
"""{target} 𝐌𝚄𝙹𝙴 𝐄𝙺 𝐁𝙰𝙰𝚃 𝐁𝙰𝚃𝙰 𝐒𝙰𝙱𝚂𝙴 𝐉𝚈𝙰𝙳𝙰 𝐌𝙰𝚉𝙰 𝐓𝙴𝚁𝙸 𝐌𝙰𝙰 𝐎𝐑 𝐁𝙰𝙷𝙴𝙽 𝐊𝙾 𝐂𝙷𝙾𝙳𝙽𝙴 𝐌𝙰𝙸 𝐀𝚃𝙰 𝐇𝙰𝙸 𝐘𝙰 𝐅𝙸𝚁 𝐓𝙴𝚁𝙸 𝐁𝙰𝙽𝙳𝙸 𝐂𝙷𝙾𝙳𝙽𝙴 𝐌𝙰𝙸??💆🍃""",
"""{target} 𝐓𝙴𝚁𝙴 𝐒𝙲𝙷𝙾𝙾𝙻 𝐊𝙴 𝐃𝙾𝚂𝚃 𝐊𝙴𝙷𝚃𝙴 𝐓𝙷𝙴 𝐉𝙰𝙱 𝐔𝙽𝙺𝙴 𝐏𝙰𝚂𝚂 𝐑𝙰𝙽𝙳𝙸 𝐂𝙷𝙾𝙳𝙽𝙴 𝐊𝙴 𝐏𝙰𝙸𝚂𝙴 𝐍𝙰𝙷𝙸 𝐓𝙷𝙴 𝐓𝙰𝙱 𝐓𝙴𝚁𝙸 𝐆𝙸𝚁𝙻𝙵𝚁𝙴𝙽𝙳 𝐔𝙽𝙺𝙸 𝐆𝙷𝙾𝙳𝙸 𝐁𝙰𝙽𝙺𝙴 𝐅𝐑𝐄𝐄 𝙼𝙰𝙸 𝚄𝙽𝙷𝙴 𝙼𝙰𝚉𝙴 𝙺𝙰𝚁𝚆𝙰𝚃𝙸 𝐓𝙷𝙸!!. 𝐊𝚈𝙰 𝐘𝙴 𝐒𝙰𝙲𝙷 𝐁𝙰𝙰𝚃 𝐇𝙰𝙸?🥰💗""",
"""{target} 𝐊𝙴 𝐒𝚄𝙿𝙿𝙾𝚁𝚃𝙴𝚁𝚂 𝐓𝚄𝙼 {target}  𝐊𝙾 𝐈𝚂𝙸 𝐋𝙸𝚈𝙴 𝐒𝚄𝙿𝙿𝙾𝚁𝚃 𝐊𝙰𝚁𝚃𝙴 𝐇𝙾𝙽𝙰 𝐓𝙰𝙺𝙸 𝐓𝚄𝙼𝙷𝙴 {target} 𝐊𝙸 𝐌𝙰𝙰𝙺𝙸 𝐂𝙷𝚄𝚃 𝐌𝐈𝐋 𝚂𝙰𝙺𝙴?😝🤌""",
"""{target} 𝐌𝐄𝐍𝐄 𝚂𝚄𝙽𝙰 𝐇𝙰𝙸 𝐓𝐔 𝐏𝙴𝙷𝙻𝙴 𝐀𝙿𝙽𝙸 𝐌𝚄𝙼𝙼𝚈 𝐊𝙸 𝐇𝙴𝙻𝙿 𝐊𝙰𝚁𝚃𝙰 𝐓𝙷𝙰 𝐌𝙾𝙽𝙀𝚈 𝐆𝚁𝙸𝙽𝙳 𝐊𝙰𝚁𝚃𝙰 𝐓𝐇𝐀? \n  𝐊𝚈𝙰 𝐌𝙰𝚃𝙻𝙰𝙱 {target}  𝐍𝙴 𝐆𝙷𝙾𝙳𝙸 𝐁𝙰𝙽𝙽𝙰 𝐀𝐏𝐍𝐈 𝐌𝐀𝐀 𝐒𝙴 𝐒𝙸𝙺𝙷𝙰 𝐇𝐀𝐈💀 😓🤢""",
"""{target} 𝐓𝙴𝚁𝙴 𝐅𝙰𝙼𝙸𝙻𝚈 𝐊𝙸 𝐆𝙰𝚁𝙸𝙱𝙸 𝐃𝙴𝙺𝙷 𝐊𝙰𝚁 𝐓𝐎 𝐑𝙾𝙰𝙳 𝐏𝙴 𝐁𝙴𝚃𝙷𝙽𝙴 𝐖𝙰𝙻𝙰 𝚅𝙾 𝐁𝙷𝙸𝙺𝙰𝚁𝙸 𝐉𝐈𝐒𝐊𝐄 𝐊𝐀𝐓𝐎𝐑𝐄 𝙼𝙰𝙸 𝟸 𝐑𝐔𝐏𝐄𝐘 𝚂𝙴 𝙺𝚄𝙲𝙷 𝐉𝐘𝐀𝐃𝐀 𝙽𝙰𝙷𝙸 𝐇𝐀𝐈 𝚅𝙾 𝐀𝐌𝐄𝐄𝐑 𝙻𝙰𝙶𝚃𝙰 𝐇𝐀𝐈😢😂🤣""",
"""{target} 𝐀𝙰𝙿𝙺𝙸 𝐌𝙰𝙰 𝐂𝙷𝚄𝐃 𝐑𝙰𝐇𝐈 𝐇𝙰𝙸 𝑺ʏ𝑳ᴀs 𝚂𝙴 𝐓𝐎𝐇 𝙰𝙱 𝐀𝙿𝙺𝙾 𝐊𝙰𝙸𝚂𝙰 𝐋𝐀𝐆𝐑𝐀 𝐇𝐀𝐈?🌚🍀""",
"""{target} 𝐓𝙴𝚁𝙴 𝐊𝙷𝙰𝚂 𝐃𝙾𝚂𝚃 𝙽𝐄 𝐊𝙰𝙷𝙰 𝐓𝚄 𝐑𝐎𝐙 𝚂𝙰𝙱𝙺𝙰 𝐋𝐎𝐃𝐀 𝙼𝚄𝙷 𝙼𝙰𝙸 𝙻𝙴𝙺𝙴𝚁 𝐌𝐀𝚉𝙴 𝚂𝙴 𝐂𝐇𝐔𝐒𝐓𝙰 𝙷𝙰𝙸😹👻""",
"""{target} 𝐌𝚄𝙹𝙴 𝐒𝚄𝙽𝙽𝙴 𝐌𝙰𝙸 𝐀𝚈𝙰 𝐇𝙰𝙸 𝐓𝐔 𝟷𝟶 𝐑𝐔𝐏𝐄𝐘 𝙼𝙰𝙸 𝐀𝐏𝙽𝙴 𝐂𝙷𝚄𝙲𝙷𝙀(  ·  )(  ·  ) 𝐃𝙰𝙱𝙰𝙽𝙴 𝐃𝙴𝚃𝙰 𝐇𝙰𝙸😍""",
"""{target} 𝐁𝙷𝙰𝙸 𝐉𝐀𝐁 𝙻𝙾𝙶 𝐌𝙰𝚉𝙴 𝐌𝙰𝚉𝙴 𝐌𝙰𝙸 𝐀𝙰𝙿𝙺𝙸 𝐆𝙰𝙰𝙽𝙳 𝐏𝚁 𝐓𝙷𝙰𝙿𝙿𝙰𝙳 𝐌𝙰𝚁𝙺𝙴 𝐉𝙰𝙰𝚃𝙴 𝐇𝙰𝙸 🍑👋 𝐓𝙾 𝐊𝙰𝙸𝚂𝙰 𝐅𝙴𝙴𝙻 𝐇𝙾𝚃𝙰 𝙰𝙰𝙿𝙺𝙾?😂""",
"""{target} 𝐁𝙷𝙰𝙸 𝐌𝚄𝙹𝙴 𝐀𝙿𝙺𝙴 𝐌𝚄𝙼𝙼𝚈 𝐍𝙴 𝐁𝙰𝚃𝙰𝚈𝙰 𝐊𝙸 𝐀𝙰𝙿 𝐁𝚁𝙰 👙𝐏𝙰𝙷𝙴𝙽𝚃𝙴 𝐇𝙾.!! 𝐊𝚈𝙰 𝐘𝙴 𝐁𝙰𝙰𝚃 𝐒𝙰𝙲𝙷 𝐇𝙰𝙸?👽""",
"""{target} 𝐂𝙷𝙰𝙻 𝐀𝐁 𝐁𝙷𝙾𝚃 𝐇𝚄𝙰 𝐓𝐄𝐑𝐈 𝐌𝐀𝐀 𝐋𝐎𝐃𝐄 𝐏𝐄😍  """,
"""  {target} 𝐓𝙴𝚁𝙸 𝐌𝙰𝙺𝙴 𝐑𝙰𝙽𝙶𝙸𝙽 𝐌𝙾𝙾𝐃 𝐏𝐑 𝙼𝙰𝙸 𝙰𝙿𝙽𝙴 𝐋𝐎𝐃𝐄 𝐒𝐄 𝐏𝐈𝐂𝐇𝐊𝐀𝐑𝐈 𝐌𝐀𝐑𝐃𝐔?🤣""",
"""{target} 𝐂𝐇𝐀𝐋 𝐓𝐌𝐊𝐂  𝐀𝐏𝐍𝐄 पिता जी 𝑺ʏ𝑳ᴀs 𝐆0ᴅ 𝐊𝐎 𝚂𝙰𝙻𝙰𝙼 𝐓𝙷𝙾𝙺🫡 🫶🎀""",
    "{n} 𝘍𝘈𝘜𝘑𝘐 𝘊𝘜𝘛𝘛𝘐𝘕𝘎 𝘞𝘈𝘓𝘌 𝘏𝘐𝘑𝘋𝘌 𝘗𝘌𝘏𝘓𝘌 𝘑𝘈𝘒𝘌 𝘈𝘗𝘕𝘐 𝘔𝘈𝘒𝘌 𝘑𝘏𝘈𝘛 𝘒𝘌 𝘉𝘈𝘈𝘓𝘖𝘕 𝘒𝘖 𝘞𝘖𝘓𝘍 𝘊𝘜𝘛 𝘒𝘙𝘞𝘈 😁🤟🏻💥❤️",
    "{n} 𝘉𝘢𝘤𝘩𝘬𝘦 𝘙𝘦𝘩𝘯𝘢 𝘉𝘦𝘵𝘢 𝘞𝘳𝘯𝘢 𝘈𝘣𝘥𝘶𝘭 𝘴𝘢𝘮𝘢𝘥 𝘒𝘐 𝘔𝘜𝘜𝘏 𝘗 𝘊𝘏𝘖𝘖𝘛 𝘙𝘈𝘎𝘈𝘋 𝘋𝘌𝘛𝘐 𝘏 🌈🤢🤮🫰🏻",
    "{n} 𝘊𝘏𝘜𝘋𝘈𝘐 𝘒𝘏𝘈𝘈 𝘔𝘋𝘊 𝘉𝘚𝘚 𝘛𝘜 🍭🍭🍭🍭",
    "{n} 𝘈𝘑𝘈 𝘛𝘙𝘠 𝘔𝘈𝘒𝘈 𝘉𝘏𝘖𝘚𝘋𝘈 𝘔𝘌𝘈𝘚𝘜𝘙𝘌 𝘒𝘙𝘜𝘕𝘎𝘈 😁🖖🏻📐📐",
    "{n} 𝘙𝘕𝘋𝘠𝘒𝘌 𝘊𝘈𝘓𝘓 𝘍𝘠𝘛𝘌𝘙 𝘉𝘈𝘕𝘌𝘎𝘈 𝘌𝘒 𝘙𝘌𝘏𝘗𝘈𝘛 𝘔 𝘙𝘈𝘗𝘌 𝘒𝘙𝘋𝘌𝘕𝘎𝘌 𝘛𝘌𝘙𝘈 ❄️🫰🏻🚓🚨💘😅",
    "{n} 𝘛𝘦𝘳𝘪 𝘔𝘢𝘬𝘢 𝘏𝘰𝘳𝘴𝘦𝘱𝘰𝘸𝘦𝘳 𝘒𝘩𝘢𝘬𝘦 𝘤𝘩𝘰𝘥𝘶𝘯𝘨𝘢 🩺🥼🧑🏻‍⚕️😷💉💉💊",
    "{n} 𝘛𝘶 𝘒𝘩𝘢𝘺𝘦𝘨𝘢 𝘗𝘪𝘻𝘻𝘢 𝘛𝘳𝘺𝘮𝘢𝘊𝘰 𝘊𝘩𝘰𝘥??𝘨𝘢 𝘚𝘺𝘓𝘢𝘴 𝘡𝘪𝘻𝘢🪼🐳🦋🫐🍕😁",
    "{n} Ab 𝘔𝘦𝘳𝘢 𝘏𝘌𝘈𝘙𝘛 𝘉𝘙𝘌𝘈𝘒 𝘏𝘎𝘠𝘈 𝘛𝘙𝘠𝘔𝘈𝘉𝘏𝘌𝘕 𝘒𝘖 𝘚𝘈𝘋 𝘚𝘖𝘕𝘎 𝘒𝘐 𝘗𝘓𝘈𝘠𝘓𝘐𝘚𝘛 𝘓𝘈𝘎𝘈 𝘒𝘌 𝘊𝘖𝘋𝘜𝘕𝘎𝘈 😫😵😵‍💫🫨🥴🥵🥶👿🤡💩",
]

RR_MSG = [
    "oi 𝐓ᴇʀɪ 𝐌‌ᴀᴀ गुलाम ₰🖤",
    "⋆⭒˚.⋆🔭 𝐒ʜᴜᴛ 𝐔ᴘ 𝐑ᴀɴᴅɪᴋᴇ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐂ʜᴜᴅᴀɪ 𝐄ɴᴊᴏʏ 𝐊ʀ 𝐑ᴀʜᴀ 𝐓ᴇʟᴇ𝐒ᴄᴏᴘᴇ 𝐒ᴇ⋆⭒˚.⋆🔭",
    "𝐓ᴇʀʏ 𝐁ʜᴇ𝐍 𝐊ᴇ ( ͜。 ㅅ ͜。)🥛 ʏᴜᴍᴍʏ",
    "Shut up रंडीके वरना दुनिया यही बोलेगी तेरी बहन Chod",
    "⚡𝐓ᴇʀɪ 𝐛ʜᴇɴ 𝐤ᴏ 𝐜𝐨𝐬²θ+𝐬𝐢𝐧²θ=𝟏 𝐥ᴀɢᴀᴋʀ 𝐜ᴏᴅᴜɴɢᴀ⚡",
    "Bᴇᴛᴀ Gᴀʟᴀᴛ Jᴀᴡᴀʙ Aʙ Tᴇʀɪ Mᴀ Kɪ Cʜᴜᴅᴀʏɪ Hᴏɢɪ 😁🙌🏻🔥",
     "𝐒ᴀʏ 𝑆ʏ𝐿ᴀs 𝐃ᴀᴅʏ 𓆩💗𓆪",
    "𝐖ᴏ ʙʜɪ ᴋʏᴀ ᴅɪɴ ᴛʜᴇ ᴊᴀʙ ᴛʀʏ ᴍᴀᴀ ᴍᴜᴊʜᴇ 𝐀ᴘɴᴀ 𝐂ʜᴜᴛ 𝐃ᴇᴛɪ ᴛʜɪ ʏᴀᴀʀ 💔🥀👌🏻",
    "𝐀ᴡᴀᴢ 𝐍ɪᴄʜᴇ 𝐆ᴜʟᴀᴀᴍ 🤢👇🏻",
    "𝐓ʀʏ 𝐌ᴀᴀ ɴᴇ 𝐂ʜᴜᴅɴᴇ 𝐌ᴀɪ ɢᴏʟᴅ 𝐌ᴇᴅᴀʟ 𝐉ᴇᴇᴛᴀ ᴇʏ 𝐃ᴏꜱᴛ 🤩👑",
    "𝐓ᴇʀɪ 𝐌ᴀᴀ ᴋɪ 𝐂ʜᴜᴛ 𝐌ᴇ 𝐌ᴇʀᴀ 𝐋ᴜɴᴅ 🖕🏻😈",
    "𝐁ʜᴏꜱᴀᴅɪᴋᴇ 𝐀ᴘɴɪ 𝐁ᴇʜᴇɴ 𝐂ʜᴜᴅᴀ 🖕🏻😈",
    "𝐑ᴀɴᴅɪ ᴋᴇ 𝐁ᴀᴄᴄʜᴇ 𝐀ᴜᴋᴀᴛ 𝐌ᴇ 𝐑ᴇʜ 🖕🏻😈",
    "𝐌ᴀᴅᴀʀᴄʜᴏᴅ 𝐓ᴇʀɪ 𝐌ᴀᴀ ᴋɪ 𝐂ʜᴜᴛ 🖕🏻😈",
    "𝐓ᴇʀɪ 𝐌ᴀᴀ ᴋᴀ 𝐁ʜᴏꜱᴅᴀ ᴋʜᴏʟ ᴅᴜɴɢᴀ 🔓😈",
    "𝐁ʜᴇɴᴄʜᴏᴅ 𝐀ᴘɴɪ 𝐀ᴜᴋᴀᴛ 𝐌ᴇ 𝐑ᴇʜ 🤡💩",
    "𝐓𝐌𝐊𝐂 ᴘᴇ 𝐂ʜᴀᴘᴘᴀʟ 𝐌ᴀᴀʀᴜɴɢᴀ 👟💥",
    "𝐁ʜᴏꜱᴅɪᴋᴇ 𝐓ᴇʀɪ 𝐊ʜᴀɴᴅᴀɴ ᴋɪ 𝐁𝐊𝐂 💀🖕🏻",
    "𝐑ᴀɴᴅɪ ᴋɪ 𝐀ᴜʟᴀᴅ ᴄʜᴜᴘ ʜᴏ ᴊᴀ 🔇😒",
    "𝐆ᴜʟᴀᴀᴍ ʜᴇɪ ᴛᴜ ᴍᴇʀᴀ ᴀʙ ᴀᴜʀ ʀᴀʜᴇɢᴀ ʙʜɪ 👑😎",
    "𝐓ᴇʀɪ 𝐁ᴇʜᴇɴ ᴋɪ 𝐂ʜᴜᴛ 𝐌ᴇ 𝐌ɪʀᴄʜɪ 🌶️🖕🏻",
    "𝐌ᴀᴅᴀʀᴄʜᴏᴅ 𝐓ᴇʀɪ 𝐌ᴀᴀ ᴋɪ 𝐂ʜᴜᴛ 𝐌ᴇ 𝐏ᴀɪʀ 🦶🏻😈",
    "𝐁ʜᴏꜱᴀᴅɪᴋᴇ 𝐓ᴇʀɪ 𝐁ᴇʜᴇɴ ᴋᴀ 𝐁ʜᴏꜱᴅᴀ 🗑️😏",
    "𝐑ᴀɴᴅɪ ᴋᴀ 𝐏ɪʟʟᴀ ʜᴀɪ ᴛᴜ 🐕💩",
    "𝐓ᴇʀɪ 𝐌ᴀᴀ ᴋᴏ 𝐁ᴀᴢᴀᴀʀ 𝐌ᴇ 𝐂ʜᴏᴅᴜɴɢᴀ 🌃😈",
    "𝐓ᴇʀɪ 𝐌ᴀᴀ ᴋɪ 𝐂ʜᴜᴛ 𝐌ᴇ 𝐆ᴀʀᴀᴍ 𝐓ᴇʟ 🌡️🖕🏻",
    "𝐌ᴀᴅᴀʀᴄʜᴏᴅ 𝐓ᴇʀɪ 𝐁ᴇʜᴇɴ ᴍᴇʀɪ 𝐑ᴀɴᴅɪ 💋??",
    "𝐑ᴀɴᴅɪ ᴋᴇ 𝐁ᴀᴄᴄʜᴇ 𝐓ᴇʀɪ 𝐌ᴀᴀ ᴋɪ 𝐂ʜᴜᴛ 🖕🏻😈",
    "𝐓ᴇʀɪ 𝐁ᴇʜᴇɴ ᴋᴏ 𝐑ᴀᴀᴛ ʙʜᴀʀ 𝐂ʜᴏᴅᴜɴɢᴀ 🌙😈",
    "𝐑ᴀɴᴅɪ ᴋᴀ 𝐁ᴀᴄᴄʜᴀ ʜᴀɪ ᴛᴜ ꜱᴀᴀʟᴇ 🤡💀",
    "𝐓ᴇʀɪ 𝐌ᴀᴀ ᴋɪ 𝐂ʜᴜᴛ 𝐌ᴇ 𝐌ᴇʀᴀ 𝐉ᴏᴏᴛᴀ 👞🖕🏻",
    "𝑆ʏ𝐿ᴀs 𝐃ᴀᴅʏ ᴋᴀ 𝐆ᴜʟᴀᴀᴍ ʜᴀɪ ᴛᴜ 🥀😤",
    "ᴊɪꜱ ᴅɪɴ ᴛᴜ ᴘᴀɪᴅᴀ ʜᴜᴀ 𝐓ᴇʀɪ 𝐌ᴀᴀ ɴᴇ ꜱᴏᴄʜᴀ ᴛʜᴀ ᴋᴀꜱʜ ᴀʙᴏʀᴛ ᴋᴀʀ ᴅᴇᴛɪ 💀🥀",
    "𝐀ᴘɴɪ 𝐀ᴜᴋᴀᴛ ᴅᴇᴋʜ ᴋᴜᴛᴛᴇ 🐕😂",
    "𝐆ᴀʟɪ ᴋᴀ 𝐊ᴜᴛᴛᴀ ʜᴀɪ ᴛᴜ 🐕🗑️",
    "𝐓ᴇʀɪ 𝐌ᴀᴀ ɴᴇ ᴍᴜᴊʜᴇ ᴅᴇᴋʜ ᴋᴇ ꜱᴏᴄʜᴀ ᴋᴀꜱʜ ʏᴇ ᴍᴇʀᴀ ʙᴇᴛᴀ ʜᴏᴛᴀ 🫦😏",
    "𝐂ʜᴜᴘ ᴋᴀʀ 𝐌ᴀᴅᴀʀᴄʜᴏᴅ ᴛᴇʀɪ ᴀᴜᴋᴀᴛ ɴᴀʜɪ ᴍᴇʀᴇ ꜱᴀᴀᴍɴᴇ ʙᴏʟɴᴇ ᴋɪ 🤐💀",
    "𝐓ᴇʀɪ 𝐌ᴀᴀ ᴋɪ 𝐂ʜᴜᴅᴀɪ ᴍᴇ ᴊᴀʙ ᴍᴀɪ ᴛʜᴀ ᴛᴏ ᴛᴜ ᴘᴀɪᴅᴀ ʜᴜᴀ 💀😂",
    "𝐁ʜᴀɢ ʏᴀʜᴀɴ ꜱᴇ ᴋᴜᴛᴛᴇ ᴋᴇ ᴘɪʟʟᴇ 🐕💨",
    "𝐓ᴇʀɪ 𝐁ᴇʜᴇɴ ᴋɪ ꜱᴀᴅɪ 𝐌ᴇ ᴍᴇʀᴀ ʟᴜɴᴅ 💍😈",
    "𝐌ᴀᴅᴀʀᴄʜᴏᴅ ᴀᴘɴɪ 𝐌ᴀᴀ ᴍᴀᴛ ᴄʜᴜᴅᴀ 🖕🏻👹",
    "𝐁ʜᴇɴᴄʜᴏᴅ 𝐓ᴇʀɪ 𝐊ʜᴀɴᴅᴀɴ ᴋɪ 𝐁𝐊𝐂 💀🖕🏻",
    "𝐁𝐊𝐂 🦴🐕",
]

RSPAM_MSG = [
    "⁀✘[ {target} ] के पिता श्री 𝑺ʏ𝑳ᴀs -🫵😂/~✘✘",
"⁀✘[ {target} ] के पिता श्री 𝑺ʏ𝑳ᴀs -🫵😂/~✘𓆪",
"⁀✘[ {target} ] के पिता श्री 𝑺ʏ𝑳ᴀs -🫵😂/~✘✘_",
"⁀✘[ {target} ] के पिता श्री 𝑺ʏ𝑳ᴀs -🫵😂/~✘_",
"⁀✘[ {target} ] के पिता श्री 𝑺ʏ𝑳ᴀs -🫵😂/~✘𓆪_",
"⁀✘[ {target} ] के पिता श्री 𝑺ʏ𝑳ᴀs -🫵😂/~✘⁀➴",
"⁀✘[ {target} ] के पिता श्री 𝑺ʏ𝑳ᴀs -🫵😂/~✘⁀✘",
"⁀✘[ {target} ] के पिता श्री 𝑺ʏ𝑳ᴀs -🫵😂/~✘⁀/",
"⁀✘[ {target} ] के पिता श्री 𝑺ʏ𝑳ᴀs -🫵😂/~✘✘",
"⁀✘[ {target} ] के पिता श्री 𝑺ʏ𝑳ᴀs -🫵😂/~✘𓆪",
]


# ═══════════════ 𝐇𝐄𝐋𝐏𝐄𝐑𝐒 ═══════════════
def is_admin(uid):
    return uid in ADMIN_IDS

async def safe_edit(m, t):
    try:
        await m.edit_text(t)
    except:
        pass

async def auto_del(m, d=AUTO_DEL):
    try:
        await asyncio.sleep(d)
        await m.delete()
    except:
        pass


# ═══════════════ 𝐒𝐄𝐒𝐒𝐈𝐎𝐍 ═══════════════
def save_session(s):
    with open(SESSION_FILE, "w") as f:
        f.write(s)

def load_session():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE) as f:
            return f.read().strip()
    return ""

async def create_session():
    print(mf("\nFIRST TIME LOGIN"))
    phone = input(mf("Phone: ")).strip()
    client = TelegramClient(StringSession(), API_ID, API_HASH)
    await client.connect()
    try:
        sent = await client.send_code_request(phone)
        code = input(mf("OTP: ")).strip()
        try:
            await client.sign_in(phone=phone, code=code, phone_code_hash=sent.phone_code_hash)
        except SessionPasswordNeededError:
            await client.sign_in(password=input(mf("2FA: ")).strip())
        ss = client.session.save()
        save_session(ss)
        print(mf("Session saved!\n"))
        await client.disconnect()
        return ss
    except Exception as e:
        print(f"❌ {e}")
        sys.exit(1)

async def get_session():
    s = load_session()
    if s:
        try:
            c = TelegramClient(StringSession(s), API_ID, API_HASH)
            await c.connect()
            if await c.is_user_authorized():
                await c.disconnect()
                print(mf("Session OK\n"))
                return s
            await c.disconnect()
        except:
            pass
    return await create_session()

async def get_bot_usernames():
    u = []
    for t in BOT_TOKENS:
        try:
            b = Bot(t)
            i = await b.get_me()
            u.append(i.username)
            await b.close()
        except:
            pass
    return u


# ═══════════════ 𝐍𝐂 𝐆𝐄𝐍𝐄𝐑𝐀𝐓𝐎𝐑𝐒 ═══════════════
def gen_nc(n):
    return f"{n} 12:382:{random.randint(100,999)} [{random.choice(NC_TIME_EMOJIS)}] {random.choice(NC_TIME_END)}"

def gen_nc2(n):
    e = random.choice(NC2_EMOJIS)
    return f"{n} {e}❯❯❯❯❯❯❯❯❯❯❯{e} {random.choice(NC2_END)}"

def gen_nc3(n):
    return f"〔 {n} 〕" + "𒐭"*60 + f" {random.choice(NC3_END)}"

def gen_sylasnc(n):
    e = random.choice(SYLASNC_EMOJIS)
    msg = random.choice(SYLASNC_MSGS)
    return msg.format(n=n, e=e)

def gen_tridentnc(n):
    e = random.choice(TRIDENT_EMOJIS)
    msg = random.choice(TRIDENT_MSGS)
    return msg.format(target=n, e=e)

def gen_sync(n):
    sym = random.choice(SYNC_SYMBOLS)
    em = random.choice(SYNC_EMOJIS)
    end = random.choice(SYNC_END)
    return f"〔 {n} 〕{sym*9}{em}{sym*9}{em}{sym*9}{em}{sym*9}{em}{sym*9}{em}{sym*9}{em}{sym*9}{em}{sym*9}{em}{sym*9}{em} {end}"


# ═══════════════ 𝐍𝐂 𝐖𝐎𝐑𝐊𝐄𝐑 ═══════════════
async def nc_worker(bot_app, chat_id, name, task_id, gen_func):
    while NC_TASKS.get(task_id, {}).get('running', False):
        try:
            title = gen_func(name)
            await bot_app.bot.set_chat_title(chat_id, title)
            GLOBAL_STATS["name_changes"] += 1
            await asyncio.sleep(NC_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(int(e.retry_after) + random.uniform(0, 0.5))
        except:
            await asyncio.sleep(NC_DELAY)

async def start_nc(update, context, name, gen_func, style):
    chat_id = update.effective_chat.id
    if chat_id in NC_TASKS and NC_TASKS[chat_id]['running']:
        NC_TASKS[chat_id]['running'] = False
        await asyncio.sleep(1)
        for w in NC_TASKS[chat_id].get('workers', []):
            w.cancel()
    NC_TASKS[chat_id] = {'name': name, 'running': True, 'workers': []}
    workers = 0
    for bot_app in ALL_BOT_APPS:
        task = asyncio.create_task(nc_worker(bot_app, chat_id, name, chat_id, gen_func))
        NC_TASKS[chat_id]['workers'].append(task)
        workers += 1
    await update.message.reply_text(
        mf(f"🔄 {style} STARTED!\n📛 {name}\n👷 {workers} bots\n🛑 /stopnc")
    )


# ═══════════════ 𝐒𝐏𝐀𝐌 𝐖𝐎𝐑𝐊𝐄𝐑 (𝐎𝐏𝐓𝐈𝐌𝐈𝐙𝐄𝐃) ═══════════════
async def spam_worker(bot_app, chat_id, name, task_id):
    count = 0
    while SPAM_TASKS.get(task_id, {}).get('running', False):
        try:
            delay = CHAT_DELAYS.get(chat_id, 0)
            msg = SPAM_MSG[count % len(SPAM_MSG)].format(target=name)
            await bot_app.bot.send_message(chat_id=chat_id, text=msg)
            count += 1
            GLOBAL_STATS["messages_sent"] += 1
            if delay > 0:
                await asyncio.sleep(delay)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(int(e.retry_after) + random.uniform(0, 1))
        except (TimedOut, NetworkError):
            await asyncio.sleep(0.5)
        except Exception as e:
            if "flood" in str(e).lower():
                m = re.search(r'retry in (\d+)', str(e).lower())
                if m:
                    await asyncio.sleep(int(m.group(1)) + 2)
                else:
                    await asyncio.sleep(30)
            else:
                await asyncio.sleep(0.5)


# ═══════════════ 𝐑𝐒𝐏𝐀𝐌 𝐖𝐎𝐑𝐊𝐄𝐑 ═══════════════
async def rspam_worker(bot_app, chat_id, name, msg_id, task_id):
    count = 0
    while RSPAM_TASKS.get(task_id, {}).get('running', False):
        try:
            delay = CHAT_DELAYS.get(chat_id, 0)
            msg = RSPAM_MSG[count % len(RSPAM_MSG)].format(target=name)
            await bot_app.bot.send_message(
                chat_id=chat_id,
                text=msg,
                reply_to_message_id=msg_id
            )
            count += 1
            GLOBAL_STATS["rspam_sent"] += 1
            if delay > 0:
                await asyncio.sleep(delay)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(int(e.retry_after) + random.uniform(0, 1))
        except (TimedOut, NetworkError):
            await asyncio.sleep(0.5)
        except Exception as e:
            if "flood" in str(e).lower():
                m = re.search(r'retry in (\d+)', str(e).lower())
                if m:
                    await asyncio.sleep(int(m.group(1)) + 2)
                else:
                    await asyncio.sleep(30)
            else:
                await asyncio.sleep(0.5)


# ═══════════════ 𝐑𝐄𝐏𝐋𝐘 𝐖𝐎𝐑𝐊𝐄𝐑 ═══════════════
async def reply_worker(bot_app, chat_id, name, task_id, is_rr=False):
    pending_dict = PENDING_RR if is_rr else PENDING_REPLIES
    msg_list = RR_MSG if is_rr else REPLY_MSG
    tasks_dict = RR_TASKS if is_rr else REPLY_TASKS
    while tasks_dict.get(task_id, {}).get('running', False):
        try:
            if chat_id in pending_dict and pending_dict[chat_id]:
                msg_id = pending_dict[chat_id].pop(0)
                text = random.choice(msg_list).format(target=name)
                await bot_app.bot.send_message(chat_id=chat_id, text=text, reply_to_message_id=msg_id)
                GLOBAL_STATS["replies_sent"] += 1
                await asyncio.sleep(0.3)
            else:
                await asyncio.sleep(0.5)
        except asyncio.CancelledError:
            break
        except:
            await asyncio.sleep(0.5)


# ═══════════════ 𝐄𝐌𝐎𝐉𝐈 𝐑𝐀𝐈𝐍 𝐖𝐎𝐑𝐊𝐄𝐑 ═══════════════
async def emoji_worker(bot_app, chat_id, emoji, task_id):
    while EMOJI_TASKS.get(task_id, {}).get('running', False):
        try:
            delay = CHAT_DELAYS.get(chat_id, 0)
            line = emoji * 30
            block = "\n".join([line] * 15)
            await bot_app.bot.send_message(chat_id=chat_id, text=block)
            GLOBAL_STATS["messages_sent"] += 1
            if delay > 0:
                await asyncio.sleep(delay)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(int(e.retry_after) + random.uniform(0, 1))
        except:
            await asyncio.sleep(0.5)


# ═══════════════ 𝐓𝐓𝐒 𝐒𝐏𝐀𝐌 𝐖𝐎𝐑𝐊𝐄𝐑 ═══════════════
async def ttsspam_worker(bot_app, chat_id, text, voice_type, task_id):
    count = 0
    while TTSSPAM_TASKS.get(task_id, {}).get('running', False):
        try:
            delay = CHAT_DELAYS.get(chat_id, 0)
            path = os.path.join(tempfile.gettempdir(), f"ttsspam_{chat_id}_{random.randint(1000,9999)}.mp3")
            
            if voice_type == "anime":
                communicate = edge_tts.Communicate(text, "ja-JP-NanamiNeural")
                await communicate.save(path)
            else:
                loop = asyncio.get_running_loop()
                def gen():
                    tts = gTTS(text=text, lang='hi')
                    tts.save(path)
                await loop.run_in_executor(None, gen)
            
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    await bot_app.bot.send_voice(chat_id=chat_id, voice=f, caption=f"💣 {text[:50]}")
                
                try:
                    os.remove(path)
                except:
                    pass
            
            count += 1
            GLOBAL_STATS["messages_sent"] += 1
            if delay > 0:
                await asyncio.sleep(delay)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(int(e.retry_after) + random.uniform(0, 1))
        except:
            await asyncio.sleep(0.5)


# ═══════════════ 𝐏𝐈𝐂𝐒𝐏𝐀𝐌 𝐖𝐎𝐑𝐊𝐄𝐑 ═══════════════
async def picspam_worker(bot_app, chat_id, file_id, task_id):
    while PICSPAM_TASKS.get(task_id, {}).get('running', False):
        try:
            delay = CHAT_DELAYS.get(chat_id, 0)
            await bot_app.bot.send_photo(chat_id=chat_id, photo=file_id)
            GLOBAL_STATS["messages_sent"] += 1
            if delay > 0:
                await asyncio.sleep(delay)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(int(e.retry_after) + random.uniform(0, 1))
        except:
            await asyncio.sleep(0.5)


# ═══════════════ 𝐏𝐅𝐏 𝐖𝐎𝐑𝐊𝐄𝐑 ═══════════════
async def pfp_worker(bot_app, chat_id, paths, task_id):
    idx = 0
    while PFP_TASKS.get(task_id, {}).get('running', False):
        try:
            delay = CHAT_DELAYS.get(chat_id, 3)
            path = paths[idx % len(paths)]
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    await bot_app.bot.set_chat_photo(chat_id=chat_id, photo=f)
            idx += 1
            await asyncio.sleep(delay)
        except asyncio.CancelledError:
            break
        except:
            await asyncio.sleep(3)


# ═══════════════ 𝐔𝐒𝐄𝐑𝐁𝐎𝐓 /𝐛𝐨𝐭𝐬 (𝐅𝐀𝐒𝐓) ═══════════════
@events.register(events.NewMessage(pattern="^/bots$"))
async def ub_bots(event):
    if not event.is_group:
        return
    if not is_admin(event.sender_id):
        await auto_del(await event.reply(mf("❌ Sirf Admin!")))
        return

    group = await event.get_chat()
    is_sg = hasattr(group, 'megagroup') or hasattr(group, 'broadcast')
    
    if is_sg:
        me = await event.client.get_me()
        try:
            perm = await event.client.get_permissions(group, me)
            if not perm.is_admin:
                await event.reply(mf("❌ Userbot Ko Admin Banao!"))
                return
            if not perm.add_admins:
                await event.reply(mf("❌ Add Admins Permission Do!"))
                return
        except:
            pass

    usernames = await get_bot_usernames()
    if not usernames:
        await event.reply(mf("❌ No Valid Tokens!"))
        return

    total = len(usernames)
    st = await event.reply(mf(f"🤖 Adding {total} Bots..."))
    
    added, admin_ok, failed = 0, 0, 0
    entities = []
    
    for u in usernames:
        try:
            ent = await event.client.get_input_entity(u)
            entities.append((u, ent))
        except:
            entities.append((u, u))
    
    # Add all concurrently
    add_tasks = []
    for u, ent in entities:
        if is_sg:
            add_tasks.append(event.client(InviteToChannelRequest(group, [ent])))
        else:
            add_tasks.append(event.client(AddChatUserRequest(chat_id=group.id, user_id=ent, fwd_limit=0)))
    
    results = await asyncio.gather(*add_tasks, return_exceptions=True)
    
    for result in results:
        if isinstance(result, Exception):
            failed += 1
        else:
            added += 1
    
    await safe_edit(st, mf(f"✅ Added: {added}/{total}\n⏳ Promoting..."))
    
    # Promote all concurrently
    if is_sg:
        promote_tasks = []
        for u, ent in entities:
            promote_tasks.append(
                event.client(EditAdminRequest(
                    group, ent,
                    ChatAdminRights(
                        change_info=True, post_messages=True, edit_messages=True,
                        delete_messages=True, ban_users=True, invite_users=True,
                        pin_messages=True, add_admins=True, manage_call=True,
                    ), "Bot"
                ))
            )
        
        admin_results = await asyncio.gather(*promote_tasks, return_exceptions=True)
        
        for result in admin_results:
            if not isinstance(result, Exception):
                admin_ok += 1
    
    await safe_edit(st, mf(
        f"╔══════════════════════════╗\n"
        f"║  ✅ BOTS ADDED ✅         ║\n"
        f"╚══════════════════════════╝\n\n"
        f"🤖 Added: `{added}`\n"
        f"👑 Admin: `{admin_ok}`\n"
        f"❌ Failed: `{failed}`\n"
        f"📊 Total: `{total}`\n\n"
        f"🎉 Ab Bots /ping Respond Karenge!"
    ))
    await auto_del(st, 15)


# ═══════════════ 𝐊𝐄𝐄𝐏𝐀𝐋𝐈𝐕𝐄 𝐒𝐄𝐑𝐕𝐄𝐑 ═══════════════
async def keepalive_server():
    async def handle(request):
        return web.Response(text="OK")
    app = web.Application()
    app.router.add_get("/", handle)
    app.router.add_get("/ping", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(get_env("BOT_PORT", "3000"))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(mf(f"🌐 Keepalive Server On Port {port}"))
        
# ═══════════════ 𝐁𝐎𝐓 𝐂𝐎𝐌𝐌𝐀𝐍𝐃𝐒 ═══════════════
async def b_start(update, context):
    await update.message.reply_text(START_REPLY)

async def b_menu(update, context):
    bot = await context.bot.get_me()
    await update.message.reply_text(
        mf(
            "╭═━「 ⚜️ SYLAS INFINITY ⚜️ 」━═╮\n"
           f"        🤖 @{bot.username}\n"
            "╰═══════════════════════════════╯\n\n"
            "⌈ 🚀 MAIN ⌋\n◈ /ping /menu /music /tts /ttsja\n\n"
            "⌈ 🔧 PROFILE ⌋\n◈ /changename /changebio /changepfp\n\n"
            "⌈ 👑 ADMIN ⌋\n◈ /admin /adminoff /mute /unmute\n◈ /legarib /hatgarib /garibokilist\n\n"
            "⌈ 🔄 NC STUDIO ⌋\n◈ /nc /nc2 /nc3 /sylasnc /sylasnc2 /tridentnc /sync /stopnc\n\n"
            "⌈ 💣 ATTACK ⌋\n◈ /spam /rspam /emojis /ttsspam /ttsspamja\n◈ /stopspam /stoprspam /stopemojis /stopttsspam\n\n"
            "⌈ 💬 REPLY ⌋\n◈ /reply /stopreply /rr /stoprr\n\n"
            "⌈ 🖼️ MEDIA ⌋\n◈ /picspam /stoppicspam /pfp /stoppfp\n\n"
            "⌈ 🛠️ TOOLS ⌋\n◈ /purge /purgeall /lock /unlock\n◈ /leave /leaveall\n\n"
            "⌈ ⚙️ CONTROL ⌋\n◈ /stopall /uptime /status /react /ereact\n◈ /delay /threads\n\n"
            "⌈ 🌐 HOSTING ⌋\n◈ /addhost /mybots /removehost /hostlist\n\n"
            "╭═══════════════════════════════╮\n"
            "      ✦ SYLAS EDITION ✦\n"
            "╰═══════════════════════════════╯"
        )
    )

async def b_ping(update, context):
    bot = await context.bot.get_me()
    m = await update.message.reply_text(mf(f"🏓 Pong! [@{bot.username}] ✅"))
    await auto_del(m)


# ═══════════════ /𝐦𝐮𝐬𝐢𝐜 ═══════════════
async def b_music(update, context):
    if not update.message.text or len(update.message.text.split()) < 2:
        return
    q = update.message.text.split(maxsplit=1)[1]
    st = await update.message.reply_text(mf(f"🔍 {q}..."))
    ydl_opts = {
        'format': 'bestaudio/best', 'quiet': True, 'no_warnings': True,
        'outtmpl': os.path.join(tempfile.gettempdir(), '%(title)s.%(ext)s'),
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '128'}],
        'default_search': 'ytsearch1', 'max_filesize': MAX_AUDIO_MB*1024*1024,
    }
    try:
        loop = asyncio.get_running_loop()
        def dl():
            with yt_dlp.YoutubeDL(ydl_opts) as y:
                info = y.extract_info(f"ytsearch1:{q}", download=True)
                if 'entries' in info: info = info['entries'][0]
                fp = y.prepare_filename(info)
                mp3 = fp.rsplit('.',1)[0]+'.mp3'
                if os.path.exists(mp3): return mp3, info
                for e in ['.m4a','.webm','.opus','.mp4']:
                    alt = fp.rsplit('.',1)[0]+e
                    if os.path.exists(alt): return alt, info
                return fp, info
        fp, info = await loop.run_in_executor(None, dl)
        dur = info.get('duration',0); m,s = divmod(dur,60)
        cap = f"🎵 {info.get('title','Unknown')}\n⏱️ `{int(m)}:{int(s):02d}`"
        await st.delete()
        try: await update.message.delete()
        except: pass
        with open(fp, 'rb') as f:
            await context.bot.send_audio(update.effective_chat.id, audio=f, caption=cap)
        try: os.remove(fp)
        except: pass
    except Exception as e:
        print(f"[MUSIC] {e}")
        await auto_del(st)


# ═══════════════ /𝐟𝐢𝐧𝐝 = /𝐦𝐮𝐬𝐢𝐜 ═══════════════
async def b_find(update, context):
    await b_music(update, context)


# ═══════════════ /𝐭𝐭𝐬 (𝐅𝐢𝐱𝐞𝐝) ═══════════════
async def b_tts(update, context):
    if not context.args:
        await update.message.reply_text(mf("📌 /tts <text>\n🎌 /ttsja <text> - Anime Voice\n💣 /ttsspam <text> - TTS Spam"))
        return
    
    text = " ".join(context.args)
    chat_id = update.effective_chat.id
    msg = await update.message.reply_text(mf("🔊 Generating TTS..."))
    
    try:
        loop = asyncio.get_running_loop()
        def gen_tts():
            path = os.path.join(tempfile.gettempdir(), f"tts_{chat_id}_{random.randint(1000,9999)}.mp3")
            tts = gTTS(text=text, lang='hi')
            tts.save(path)
            return path
        
        path = await loop.run_in_executor(None, gen_tts)
        
        if not os.path.exists(path):
            raise Exception("File not created")
        
        await msg.delete()
        
        with open(path, 'rb') as f:
            await context.bot.send_voice(chat_id=chat_id, voice=f, caption=f"🗣️ {text[:100]}")
        
        try: os.remove(path)
        except: pass
        
    except Exception as e:
        print(f"[TTS] Error: {e}")
        try:
            await msg.edit_text(mf("❌ TTS Failed! Try shorter text."))
        except:
            await context.bot.send_message(chat_id=chat_id, text=mf("❌ TTS Failed! Try shorter text."))


# ═══════════════ /𝐭𝐭𝐬𝐣𝐚 - 𝐀𝐧𝐢𝐦𝐞 𝐕𝐨𝐢𝐜𝐞 ═══════════════
async def b_ttsja(update, context):
    if not context.args:
        await update.message.reply_text(mf("🎌 /ttsja <text> - Japanese Anime Voice"))
        return
    
    text = " ".join(context.args)
    chat_id = update.effective_chat.id
    msg = await update.message.reply_text(mf("🎌 Generating Anime Voice..."))
    
    try:
        path = os.path.join(tempfile.gettempdir(), f"ttsja_{chat_id}_{random.randint(1000,9999)}.mp3")
        
        communicate = edge_tts.Communicate(text, "ja-JP-NanamiNeural")
        await communicate.save(path)
        
        await msg.delete()
        with open(path, 'rb') as f:
            await context.bot.send_voice(chat_id=chat_id, voice=f, caption=f"🎌 {text[:100]}")
        try: os.remove(path)
        except: pass
    except Exception as e:
        try:
            path = os.path.join(tempfile.gettempdir(), f"ttsja_{chat_id}_{random.randint(1000,9999)}.mp3")
            tts = gTTS(text=text, lang='ja')
            tts.save(path)
            await msg.delete()
            with open(path, 'rb') as f:
                await context.bot.send_voice(chat_id=chat_id, voice=f, caption=f"🎌 {text[:100]}")
            try: os.remove(path)
            except: pass
        except:
            try: await msg.edit_text(mf("❌ Anime TTS Failed!"))
            except: pass


# ═══════════════ /𝐦𝐮𝐭𝐞 ═══════════════
async def b_mute(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNAUTH)
        return
    
    chat_id = update.effective_chat.id
    target_id = None
    
    if update.message.reply_to_message:
        target_id = update.message.reply_to_message.from_user.id
    elif context.args:
        try: target_id = int(context.args[0])
        except: pass
    
    if not target_id:
        await update.message.reply_text(mf("📌 Reply karke ya ID dekar /mute karo"))
        return
    
    try:
        await context.bot.restrict_chat_member(
            chat_id, target_id,
            permissions=ChatPermissions(can_send_messages=False)
        )
        await update.message.reply_text(mf("🔇 Muted!"))
    except Exception as e:
        await update.message.reply_text(mf(f"❌ Failed: {str(e)[:50]}"))


# ═══════════════ /𝐮𝐧𝐦𝐮𝐭𝐞 ═══════════════
async def b_unmute(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNAUTH)
        return
    
    chat_id = update.effective_chat.id
    target_id = None
    
    if update.message.reply_to_message:
        target_id = update.message.reply_to_message.from_user.id
    elif context.args:
        try: target_id = int(context.args[0])
        except: pass
    
    if not target_id:
        await update.message.reply_text(mf("📌 Reply karke ya ID dekar /unmute karo"))
        return
    
    try:
        await context.bot.restrict_chat_member(
            chat_id, target_id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_change_info=False,
                can_invite_users=True,
                can_pin_messages=False
            )
        )
        await update.message.reply_text(mf("🔊 Unmuted!"))
    except Exception as e:
        await update.message.reply_text(mf(f"❌ Failed: {str(e)[:50]}"))


# ═══════════════ 𝐏𝐑𝐎𝐅𝐈𝐋𝐄 𝐂𝐇𝐀𝐍𝐆𝐄 ═══════════════
async def b_changename(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNAUTH); return
    if not context.args:
        await update.message.reply_text(mf("📌 /changename <name>")); return
    new_name = " ".join(context.args)
    total = len(ALL_BOT_APPS)
    msg = await update.message.reply_text(mf(f"🔧 Changing Name To {new_name} For {total} Bots..."))
    changed = 0
    for bot_app in ALL_BOT_APPS:
        try: await bot_app.bot.set_my_name(name=new_name); changed += 1
        except: pass
        await asyncio.sleep(0.5)
    await msg.edit_text(mf(f"✅ Name: {new_name}\n🤖 {changed}/{total} Bots"))

async def b_changebio(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNAUTH); return
    if not context.args:
        await update.message.reply_text(mf("📌 /changebio <bio>")); return
    new_bio = " ".join(context.args)
    total = len(ALL_BOT_APPS)
    msg = await update.message.reply_text(mf(f"🔧 Changing Bio For {total} Bots..."))
    changed = 0
    for bot_app in ALL_BOT_APPS:
        try: await bot_app.bot.set_my_description(description=new_bio); changed += 1
        except: pass
        await asyncio.sleep(0.5)
    await msg.edit_text(mf(f"✅ Bio: {new_bio[:50]}\n🤖 {changed}/{total} Bots"))

async def b_changepfp(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNAUTH); return
    reply = update.message.reply_to_message
    if not reply or not reply.photo:
        await update.message.reply_text(mf("📌 Photo Pe Reply Karo")); return
    total = len(ALL_BOT_APPS)
    msg = await update.message.reply_text(mf(f"🔧 Changing PFP For {total} Bots..."))
    try:
        photo_file = reply.photo[-1]
        file = await context.bot.get_file(photo_file.file_id)
        photo_bytes = io.BytesIO()
        await file.download_to_memory(photo_bytes)
        changed = 0
        for bot_app in ALL_BOT_APPS:
            try:
                photo_bytes.seek(0)
                await bot_app.bot.set_my_photo(photo=photo_bytes)
                changed += 1
            except: pass
            await asyncio.sleep(0.8)
        photo_bytes.close()
        await msg.edit_text(mf(f"✅ PFP Changed\n🤖 {changed}/{total} Bots"))
    except Exception as e:
        await msg.edit_text(mf(f"❌ Error: {str(e)[:50]}"))


# ═══════════════ /𝐚𝐝𝐦𝐢𝐧 ═══════════════
async def b_admin(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNAUTH); return
    chat_id = update.effective_chat.id
    if not ALL_BOT_APPS:
        await update.message.reply_text(mf("❌ No Bots Active!")); return
    msg = await update.message.reply_text(mf("👑 Making All Bots Admin..."))
    promoted, already, failed = 0, 0, 0
    for bot_app in ALL_BOT_APPS:
        try:
            bot = await bot_app.bot.get_me()
            try:
                member = await context.bot.get_chat_member(chat_id, bot.id)
                if member.status in ['administrator', 'creator']: already += 1; continue
            except: pass
            await context.bot.promote_chat_member(
                chat_id=chat_id, user_id=bot.id,
                can_change_info=True,
                can_delete_messages=True,
                can_invite_users=True,
                can_restrict_members=True,
                can_pin_messages=True,
                can_promote_members=True,
                can_manage_video_chats=True,
            )
            promoted += 1; await asyncio.sleep(0.5)
        except: failed += 1
    await msg.edit_text(mf(f"✅ Promoted: {promoted}\nℹ️ Already: {already}\n❌ Failed: {failed}\n📊 Total: {len(ALL_BOT_APPS)}"))


# ═══════════════ 𝐒𝐔𝐃𝐎 𝐂𝐎𝐌𝐌𝐀𝐍𝐃𝐒 ═══════════════
async def b_legarib(update, context):
    """Owner kisi ko sudo user bana sakta hai"""
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text(mf("❌ Sirf Owner Ye Command Use Kar Sakta Hai!"))
        return
    
    target_id = None
    target_name = "Unknown"
    
    if update.message.reply_to_message:
        target_id = update.message.reply_to_message.from_user.id
        target_name = update.message.reply_to_message.from_user.first_name
    elif context.args:
        try:
            target_id = int(context.args[0])
            target_name = str(target_id)
        except:
            await update.message.reply_text(mf("📌 Reply karke ya ID dekar /legarib karo\n🔍 /garibokilist - Sudo users ki list"))
            return
    else:
        await update.message.reply_text(mf("📌 Reply karke ya ID dekar /legarib karo\n🔍 /garibokilist - Sudo users ki list"))
        return
    
    if target_id in ADMIN_IDS:
        await update.message.reply_text(mf(f"⚠️ {target_name} Pehle Se Sudo User Hai!"))
        return
    
    ADMIN_IDS.append(target_id)
    await update.message.reply_text(mf(
        f"✅ Sudo Granted!\n"
        f"👤 User: {target_name}\n"
        f"🆔 ID: {target_id}\n\n"
        f"🔓 Ab Ye /addhost Aur Saari Admin Commands Use Kar Sakta Hai!"
    ))


async def b_hatgarib(update, context):
    """Owner kisi ka sudo revoke kar sakta hai"""
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text(mf("❌ Sirf Owner!"))
        return
    
    target_id = None
    target_name = "Unknown"
    
    if update.message.reply_to_message:
        target_id = update.message.reply_to_message.from_user.id
        target_name = update.message.reply_to_message.from_user.first_name
    elif context.args:
        try:
            target_id = int(context.args[0])
            target_name = str(target_id)
        except:
            return
    else:
        await update.message.reply_text(mf("📌 Reply karke ya ID dekar /hatgarib karo"))
        return
    
    if target_id == OWNER_ID:
        await update.message.reply_text(mf("❌ Owner Ko Remove Nahi Kar Sakte!"))
        return
    
    if target_id in ADMIN_IDS:
        ADMIN_IDS.remove(target_id)
        await update.message.reply_text(mf(f"🚫 Sudo Revoked!\n👤 {target_name}\n🆔 {target_id}"))
    else:
        await update.message.reply_text(mf("ℹ️ Ye User Sudo Nahi Tha!"))


async def b_garibokilist(update, context):
    """Sudo users ki list"""
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text(mf("❌ Sirf Owner!"))
        return
    
    lines = [mf("👑 𝐆𝐀𝐑𝐈𝐁𝐎𝐊𝐈 𝐋𝐈𝐒𝐓:\n")]
    
    for i, uid in enumerate(ADMIN_IDS, 1):
        crown = "👑" if uid == OWNER_ID else "🔹"
        try:
            user = await context.bot.get_chat(uid)
            name = user.first_name
            username = f"@{user.username}" if user.username else ""
            lines.append(f"{crown} {i}. {name} {username} (`{uid}`)")
        except:
            lines.append(f"{crown} {i}. Unknown (`{uid}`)")
    
    lines.append(f"\n📊 Total Sudo: {len(ADMIN_IDS)}")
    await update.message.reply_text("\n".join(lines))


# ═══════════════ 𝐇𝐎𝐒𝐓𝐈𝐍𝐆 𝐂𝐎𝐌𝐌𝐀𝐍𝐃𝐒 ═══════════════
async def b_addhost(update, context):
    """Sudo users apna bot token add karke host kar sakte hain"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(mf("❌ Sirf Sudo Users Ye Command Use Kar Sakte Hain!"))
        return
    
    if not context.args:
        await update.message.reply_text(mf(
            "📌 /addhost <bot_token>\n"
            "🔑 BotFather se token lo aur yahan paste karo!\n"
            "✅ Tumhara bot hosted ho jayega!"
        ))
        return
    
    token = context.args[0].strip()
    user_id = str(update.effective_user.id)
    
    # Validate token
    msg = await update.message.reply_text(mf("🔍 Validating Token..."))
    
    try:
        test_bot = Bot(token)
        bot_info = await test_bot.get_me()
        await test_bot.close()
        
        # Token valid hai
        if user_id not in HOSTED_BOTS:
            HOSTED_BOTS[user_id] = []
        
        # Check if already added
        for bot in HOSTED_BOTS[user_id]:
            if bot['token'] == token:
                await msg.edit_text(mf("⚠️ Ye Bot Pehle Se Hosted Hai!"))
                return
        
        # Check max bots per sudo (5 bots)
        if len(HOSTED_BOTS[user_id]) >= 5:
            await msg.edit_text(mf("❌ Max 5 Bots Per Sudo User!"))
            return
        
        global HOSTED_BOT_COUNTER
        HOSTED_BOT_COUNTER += 1
        
        bot_data = {
            'token': token,
            'username': bot_info.username,
            'name': bot_info.first_name,
            'bot_num': HOSTED_BOT_COUNTER,
            'owner_id': user_id,
        }
        
        HOSTED_BOTS[user_id].append(bot_data)
        save_hosted_bots()
        
        # Start hosting
        task = asyncio.create_task(run_hosted_bot(token, HOSTED_BOT_COUNTER))
        
        await msg.edit_text(mf(
            f"✅ Bot Hosted Successfully!\n"
            f"🤖 @{bot_info.username}\n"
            f"📛 {bot_info.first_name}\n"
            f"👤 Owner: {update.effective_user.first_name}\n"
            f"🔢 Bot Number: {HOSTED_BOT_COUNTER}\n\n"
            f"📋 /mybots - Apne hosted bots dekho"
        ))
        
    except Exception as e:
        await msg.edit_text(mf(f"❌ Invalid Token! {str(e)[:50]}"))


async def b_mybots(update, context):
    """Sudo users apne hosted bots ki list dekh sakte hain"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(mf("❌ Sirf Sudo Users!"))
        return
    
    user_id = str(update.effective_user.id)
    
    if user_id not in HOSTED_BOTS or not HOSTED_BOTS[user_id]:
        await update.message.reply_text(mf("📋 Tumne Abhi Tak Koi Bot Host Nahi Kiya!\n🔑 /addhost <token> Se Add Karo"))
        return
    
    lines = [mf("🤖 𝐓𝐮𝐦𝐡𝐚𝐫𝐞 𝐇𝐨𝐬𝐭𝐞𝐝 𝐁𝐨𝐭𝐬:\n")]
    for i, bot in enumerate(HOSTED_BOTS[user_id], 1):
        lines.append(f"{i}. @{bot['username']} - {bot['name']}")
    
    lines.append(f"\n📊 Total: {len(HOSTED_BOTS[user_id])}")
    await update.message.reply_text("\n".join(lines))


async def b_removehost(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(mf("❌ Sirf Sudo Users!")); return
    
    if not context.args:
        await update.message.reply_text(mf("📌 /removehost <bot_username>")); return
    
    username = context.args[0].replace("@", "").strip()
    user_id = str(update.effective_user.id)
    
    if user_id not in HOSTED_BOTS:
        await update.message.reply_text(mf("❌ Tumhare Paas Koi Bot Nahi Hai!")); return
    
    for bot in HOSTED_BOTS[user_id]:
        if bot['username'] == username:
            HOSTED_BOTS[user_id].remove(bot)
            save_hosted_bots()
            await update.message.reply_text(mf(f"✅ @{username} Removed!"))
            return
    
    await update.message.reply_text(mf(f"❌ @{username} Not Found!"))


async def b_hostlist(update, context):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text(mf("❌ Sirf Owner!")); return
    
    if not HOSTED_BOTS:
        await update.message.reply_text(mf("📋 Koi Hosted Bots Nahi Hain!")); return
    
    total = 0
    lines = [mf("🌐 𝐀𝐋𝐋 𝐇𝐎𝐒𝐓𝐄𝐃 𝐁𝐎𝐓𝐒:\n")]
    
    for user_id, bots in HOSTED_BOTS.items():
        try:
            user = await context.bot.get_chat(int(user_id))
            name = user.first_name
        except:
            name = user_id
        
        lines.append(f"👤 {name}:")
        for bot in bots:
            lines.append(f"  └ @{bot['username']} - {bot['name']}")
            total += 1
    
    lines.append(f"\n📊 Total Bots: {total}")
    lines.append(f"👥 Total Users: {len(HOSTED_BOTS)}")
    
    await update.message.reply_text("\n".join(lines))

# ═══════════════ 𝐍𝐂 𝐂𝐎𝐌𝐌𝐀𝐍𝐃𝐒 ═══════════════
async def b_nc(update, context):
    if not is_admin(update.effective_user.id): await update.message.reply_text(UNAUTH); return
    if not context.args: await update.message.reply_text(mf("📌 /nc <name>")); return
    await start_nc(update, context, " ".join(context.args), gen_nc, "NC TIME")

async def b_nc2(update, context):
    if not is_admin(update.effective_user.id): await update.message.reply_text(UNAUTH); return
    if not context.args: await update.message.reply_text(mf("📌 /nc2 <name>")); return
    await start_nc(update, context, " ".join(context.args), gen_nc2, "NC2 ARROW")

async def b_nc3(update, context):
    if not is_admin(update.effective_user.id): await update.message.reply_text(UNAUTH); return
    if not context.args: await update.message.reply_text(mf("📌 /nc3 <name>")); return
    await start_nc(update, context, " ".join(context.args), gen_nc3, "NC3 BIG")

async def b_sylasnc(update, context):
    if not is_admin(update.effective_user.id): await update.message.reply_text(UNAUTH); return
    if not context.args: await update.message.reply_text(mf("🎀 /sylasnc <name>")); return
    await start_nc(update, context, " ".join(context.args), gen_sylasnc, "SYLAS NC")

async def b_sylasnc2(update, context):
    if not is_admin(update.effective_user.id): await update.message.reply_text(UNAUTH); return
    if not context.args: await update.message.reply_text(mf("❤️ /sylasnc2 <name>")); return
    await start_nc(update, context, " ".join(context.args), gen_sylasnc2, "SYLAS NC2")

async def b_tridentnc(update, context):
    if not is_admin(update.effective_user.id): await update.message.reply_text(UNAUTH); return
    if not context.args: await update.message.reply_text(mf("🔱 /tridentnc <name>")); return
    await start_nc(update, context, " ".join(context.args), gen_tridentnc, "TRIDENT NC")

async def b_sync(update, context):
    if not is_admin(update.effective_user.id): await update.message.reply_text(UNAUTH); return
    if not context.args: await update.message.reply_text(mf("☢️ /sync <name>")); return
    await start_nc(update, context, " ".join(context.args), gen_sync, "SYNC NC")

async def b_stopnc(update, context):
    if not is_admin(update.effective_user.id): await update.message.reply_text(UNAUTH); return
    chat_id = update.effective_chat.id
    if chat_id in NC_TASKS and NC_TASKS[chat_id]['running']:
        NC_TASKS[chat_id]['running'] = False; await asyncio.sleep(1)
        for w in NC_TASKS[chat_id].get('workers', []): w.cancel()
        del NC_TASKS[chat_id]; await update.message.reply_text(mf("✅ NC Stopped!"))
    else: await update.message.reply_text(mf("ℹ️ No Active NC."))


# ═══════════════ 𝐒𝐏𝐀𝐌 𝐂𝐎𝐌𝐌𝐀𝐍𝐃𝐒 ═══════════════
async def b_spam(update, context):
    if not is_admin(update.effective_user.id): await update.message.reply_text(UNAUTH); return
    if not context.args: await update.message.reply_text(mf("📌 /spam <name>")); return
    name = " ".join(context.args); chat_id = update.effective_chat.id
    if chat_id in SPAM_TASKS and SPAM_TASKS[chat_id]['running']:
        SPAM_TASKS[chat_id]['running'] = False; await asyncio.sleep(1)
        for w in SPAM_TASKS[chat_id].get('workers', []): w.cancel()
    threads = CHAT_THREADS.get(chat_id, 1)
    SPAM_TASKS[chat_id] = {'name': name, 'running': True, 'workers': []}
    workers = 0
    for bot_app in ALL_BOT_APPS:
        for _ in range(threads):
            task = asyncio.create_task(spam_worker(bot_app, chat_id, name, chat_id))
            SPAM_TASKS[chat_id]['workers'].append(task); workers += 1
    await update.message.reply_text(mf(f"💣 Spam Started!\n🎯 {name}\n👷 {workers} workers\n🛑 /stopspam"))

async def b_stopspam(update, context):
    if not is_admin(update.effective_user.id): await update.message.reply_text(UNAUTH); return
    chat_id = update.effective_chat.id
    if chat_id in SPAM_TASKS and SPAM_TASKS[chat_id]['running']:
        SPAM_TASKS[chat_id]['running'] = False; await asyncio.sleep(1)
        for w in SPAM_TASKS[chat_id].get('workers', []): w.cancel()
        del SPAM_TASKS[chat_id]; await update.message.reply_text(mf("✅ Spam Stopped!"))
    else: await update.message.reply_text(mf("ℹ️ No Active Spam."))


# ═══════════════ 𝐑𝐒𝐏𝐀𝐌 𝐂𝐎𝐌𝐌𝐀𝐍𝐃𝐒 ═══════════════
async def b_rspam(update, context):
    if not is_admin(update.effective_user.id): await update.message.reply_text(UNAUTH); return
    if not update.message.reply_to_message:
        await update.message.reply_text(mf("📌 Reply Karke /rspam <name> Bhejo")); return
    if not context.args: await update.message.reply_text(mf("📌 /rspam <name>")); return
    
    name = " ".join(context.args)
    msg_id = update.message.reply_to_message.message_id
    chat_id = update.effective_chat.id
    
    if chat_id in RSPAM_TASKS and RSPAM_TASKS[chat_id]['running']:
        RSPAM_TASKS[chat_id]['running'] = False; await asyncio.sleep(1)
        for w in RSPAM_TASKS[chat_id].get('workers', []): w.cancel()
    
    threads = CHAT_THREADS.get(chat_id, 1)
    RSPAM_TASKS[chat_id] = {'name': name, 'running': True, 'workers': []}
    RSPAM_TARGETS[chat_id] = msg_id
    workers = 0
    for bot_app in ALL_BOT_APPS:
        for _ in range(threads):
            task = asyncio.create_task(rspam_worker(bot_app, chat_id, name, msg_id, chat_id))
            RSPAM_TASKS[chat_id]['workers'].append(task); workers += 1
    await update.message.reply_text(mf(f"💣 RSPAM Started!\n🎯 {name}\n👷 {workers} workers\n🛑 /stoprspam"))

async def b_stoprspam(update, context):
    if not is_admin(update.effective_user.id): await update.message.reply_text(UNAUTH); return
    chat_id = update.effective_chat.id
    if chat_id in RSPAM_TASKS and RSPAM_TASKS[chat_id]['running']:
        RSPAM_TASKS[chat_id]['running'] = False; await asyncio.sleep(1)
        for w in RSPAM_TASKS[chat_id].get('workers', []): w.cancel()
        del RSPAM_TASKS[chat_id]
        if chat_id in RSPAM_TARGETS: del RSPAM_TARGETS[chat_id]
        await update.message.reply_text(mf("✅ RSPAM Stopped!"))
    else: await update.message.reply_text(mf("ℹ️ No Active RSPAM."))


# ═══════════════ 𝐓𝐓𝐒 𝐒𝐏𝐀𝐌 𝐂𝐎𝐌𝐌𝐀𝐍𝐃𝐒 ═══════════════
async def b_ttsspam(update, context):
    if not is_admin(update.effective_user.id): await update.message.reply_text(UNAUTH); return
    if not context.args: await update.message.reply_text(mf("📌 /ttsspam <text>\n💣 TTS Spam Attack!\n🎌 /ttsspamja <text> - Anime Spam")); return
    
    text = " ".join(context.args)
    chat_id = update.effective_chat.id
    
    if chat_id in TTSSPAM_TASKS and TTSSPAM_TASKS[chat_id]['running']:
        TTSSPAM_TASKS[chat_id]['running'] = False; await asyncio.sleep(1)
        for w in TTSSPAM_TASKS[chat_id].get('workers', []): w.cancel()
    
    threads = CHAT_THREADS.get(chat_id, 1)
    TTSSPAM_TASKS[chat_id] = {'running': True, 'workers': []}
    workers = 0
    for bot_app in ALL_BOT_APPS:
        for _ in range(threads):
            task = asyncio.create_task(ttsspam_worker(bot_app, chat_id, text, "hindi", chat_id))
            TTSSPAM_TASKS[chat_id]['workers'].append(task); workers += 1
    
    await update.message.reply_text(mf(f"💣 TTS Spam Started!\n🎯 {text[:50]}\n👷 {workers} workers\n🛑 /stopttsspam"))


async def b_ttsspamja(update, context):
    if not is_admin(update.effective_user.id): await update.message.reply_text(UNAUTH); return
    if not context.args: await update.message.reply_text(mf("🎌 /ttsspamja <text>\n🎌 Anime TTS Spam!")); return
    
    text = " ".join(context.args)
    chat_id = update.effective_chat.id
    
    if chat_id in TTSSPAM_TASKS and TTSSPAM_TASKS[chat_id]['running']:
        TTSSPAM_TASKS[chat_id]['running'] = False; await asyncio.sleep(1)
        for w in TTSSPAM_TASKS[chat_id].get('workers', []): w.cancel()
    
    threads = CHAT_THREADS.get(chat_id, 1)
    TTSSPAM_TASKS[chat_id] = {'running': True, 'workers': []}
    workers = 0
    for bot_app in ALL_BOT_APPS:
        for _ in range(threads):
            task = asyncio.create_task(ttsspam_worker(bot_app, chat_id, text, "anime", chat_id))
            TTSSPAM_TASKS[chat_id]['workers'].append(task); workers += 1
    
    await update.message.reply_text(mf(f"🎌 Anime TTS Spam Started!\n🎯 {text[:50]}\n👷 {workers} workers\n🛑 /stopttsspam"))


async def b_stopttsspam(update, context):
    if not is_admin(update.effective_user.id): await update.message.reply_text(UNAUTH); return
    chat_id = update.effective_chat.id
    if chat_id in TTSSPAM_TASKS and TTSSPAM_TASKS[chat_id]['running']:
        TTSSPAM_TASKS[chat_id]['running'] = False; await asyncio.sleep(1)
        for w in TTSSPAM_TASKS[chat_id].get('workers', []): w.cancel()
        del TTSSPAM_TASKS[chat_id]; await update.message.reply_text(mf("✅ TTS Spam Stopped!"))
    else: await update.message.reply_text(mf("ℹ️ No Active TTS Spam."))


# ═══════════════ 𝐄𝐌𝐎𝐉𝐈𝐒 𝐂𝐎𝐌𝐌𝐀𝐍𝐃 ═══════════════
async def b_emojis(update, context):
    if not is_admin(update.effective_user.id): await update.message.reply_text(UNAUTH); return
    emoji = context.args[0] if context.args else "🔥"
    chat_id = update.effective_chat.id
    if chat_id in EMOJI_TASKS and EMOJI_TASKS[chat_id]['running']:
        EMOJI_TASKS[chat_id]['running'] = False; await asyncio.sleep(1)
        for w in EMOJI_TASKS[chat_id].get('workers', []): w.cancel()
    EMOJI_TASKS[chat_id] = {'running': True, 'workers': []}
    for bot_app in ALL_BOT_APPS:
        task = asyncio.create_task(emoji_worker(bot_app, chat_id, emoji, chat_id))
        EMOJI_TASKS[chat_id]['workers'].append(task)
    await update.message.reply_text(mf(f"🌧️ Emoji Rain Started! ({emoji})\n🛑 /stopemojis"))

async def b_stopemojis(update, context):
    if not is_admin(update.effective_user.id): await update.message.reply_text(UNAUTH); return
    chat_id = update.effective_chat.id
    if chat_id in EMOJI_TASKS and EMOJI_TASKS[chat_id]['running']:
        EMOJI_TASKS[chat_id]['running'] = False; await asyncio.sleep(1)
        for w in EMOJI_TASKS[chat_id].get('workers', []): w.cancel()
        del EMOJI_TASKS[chat_id]; await update.message.reply_text(mf("✅ Emoji Rain Stopped!"))
    else: await update.message.reply_text(mf("ℹ️ No Active Emoji Rain."))
    

# ═══════════════ 𝐑𝐄𝐏𝐋𝐘 𝐂𝐎𝐌𝐌𝐀𝐍𝐃𝐒 ═══════════════
async def b_reply(update, context):
    if not is_admin(update.effective_user.id): await update.message.reply_text(UNAUTH); return
    if not context.args: await update.message.reply_text(mf("📌 /reply <name>")); return
    name = " ".join(context.args); chat_id = update.effective_chat.id
    if chat_id in REPLY_TASKS and REPLY_TASKS[chat_id]['running']:
        REPLY_TASKS[chat_id]['running'] = False; await asyncio.sleep(1)
        for w in REPLY_TASKS[chat_id].get('workers', []): w.cancel()
    REPLY_TASKS[chat_id] = {'name': name, 'running': True, 'workers': []}
    PENDING_REPLIES[chat_id] = []
    for bot_app in ALL_BOT_APPS:
        task = asyncio.create_task(reply_worker(bot_app, chat_id, name, chat_id))
        REPLY_TASKS[chat_id]['workers'].append(task)
    await update.message.reply_text(mf(f"💬 Reply Started!\n🎯 {name}\n🛑 /stopreply"))

async def b_stopreply(update, context):
    if not is_admin(update.effective_user.id): await update.message.reply_text(UNAUTH); return
    chat_id = update.effective_chat.id
    if chat_id in REPLY_TASKS and REPLY_TASKS[chat_id]['running']:
        REPLY_TASKS[chat_id]['running'] = False; await asyncio.sleep(1)
        for w in REPLY_TASKS[chat_id].get('workers', []): w.cancel()
        del REPLY_TASKS[chat_id]
        if chat_id in PENDING_REPLIES: del PENDING_REPLIES[chat_id]
        await update.message.reply_text(mf("✅ Reply Stopped!"))
    else: await update.message.reply_text(mf("ℹ️ No Active Reply."))

async def b_rr(update, context):
    if not is_admin(update.effective_user.id): await update.message.reply_text(UNAUTH); return
    if not update.message.reply_to_message: await update.message.reply_text(mf("📌 Reply Karke /rr Bhejo")); return
    target = update.message.reply_to_message.from_user
    if not target: return
    chat_id = update.effective_chat.id
    if chat_id in RR_TASKS and RR_TASKS[chat_id]['running']:
        RR_TASKS[chat_id]['running'] = False; await asyncio.sleep(1)
        for w in RR_TASKS[chat_id].get('workers', []): w.cancel()
    RR_TASKS[chat_id] = {'name': target.first_name, 'running': True, 'workers': []}
    RR_TARGETS[chat_id] = target.id; PENDING_RR[chat_id] = []
    for bot_app in ALL_BOT_APPS:
        task = asyncio.create_task(reply_worker(bot_app, chat_id, target.first_name, chat_id, is_rr=True))
        RR_TASKS[chat_id]['workers'].append(task)
    await update.message.reply_text(mf(f"🔁 RR Started!\n🎯 {target.first_name}\n🛑 /stoprr"))

async def b_stoprr(update, context):
    if not is_admin(update.effective_user.id): await update.message.reply_text(UNAUTH); return
    chat_id = update.effective_chat.id
    if chat_id in RR_TASKS and RR_TASKS[chat_id]['running']:
        RR_TASKS[chat_id]['running'] = False; await asyncio.sleep(1)
        for w in RR_TASKS[chat_id].get('workers', []): w.cancel()
        del RR_TASKS[chat_id]
        if chat_id in RR_TARGETS: del RR_TARGETS[chat_id]
        if chat_id in PENDING_RR: del PENDING_RR[chat_id]
        await update.message.reply_text(mf("✅ RR Stopped!"))
    else: await update.message.reply_text(mf("ℹ️ No Active RR."))


# ═══════════════ 𝐏𝐈𝐂𝐒𝐏𝐀𝐌 / 𝐏𝐅𝐏 ═══════════════
async def b_picspam(update, context):
    if not is_admin(update.effective_user.id): await update.message.reply_text(UNAUTH); return
    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        await update.message.reply_text(mf("📌 Reply To Photo")); return
    chat_id = update.effective_chat.id; file_id = update.message.reply_to_message.photo[-1].file_id
    if chat_id in PICSPAM_TASKS and PICSPAM_TASKS[chat_id]['running']:
        PICSPAM_TASKS[chat_id]['running'] = False; await asyncio.sleep(1)
        for w in PICSPAM_TASKS[chat_id].get('workers', []): w.cancel()
    PICSPAM_TASKS[chat_id] = {'running': True, 'workers': []}; PICSPAM_FILE_IDS[chat_id] = file_id
    for bot_app in ALL_BOT_APPS:
        task = asyncio.create_task(picspam_worker(bot_app, chat_id, file_id, chat_id))
        PICSPAM_TASKS[chat_id]['workers'].append(task)
    await update.message.reply_text(mf("🖼️ PicSpam Started!\n🛑 /stoppicspam"))

async def b_stoppicspam(update, context):
    if not is_admin(update.effective_user.id): await update.message.reply_text(UNAUTH); return
    chat_id = update.effective_chat.id
    if chat_id in PICSPAM_TASKS and PICSPAM_TASKS[chat_id]['running']:
        PICSPAM_TASKS[chat_id]['running'] = False; await asyncio.sleep(1)
        for w in PICSPAM_TASKS[chat_id].get('workers', []): w.cancel()
        del PICSPAM_TASKS[chat_id]
        if chat_id in PICSPAM_FILE_IDS: del PICSPAM_FILE_IDS[chat_id]
        await update.message.reply_text(mf("✅ PicSpam Stopped!"))
    else: await update.message.reply_text(mf("ℹ️ No Active PicSpam."))

async def b_pfp(update, context):
    if not is_admin(update.effective_user.id): await update.message.reply_text(UNAUTH); return
    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        await update.message.reply_text(mf("📌 Reply To Photo")); return
    chat_id = update.effective_chat.id
    file = await context.bot.get_file(update.message.reply_to_message.photo[-1].file_id)
    path = f"pfp_{chat_id}.jpg"; await file.download_to_drive(path)
    if chat_id in PFP_TASKS and PFP_TASKS[chat_id]['running']:
        PFP_TASKS[chat_id]['running'] = False; await asyncio.sleep(1)
        for w in PFP_TASKS[chat_id].get('workers', []): w.cancel()
    PFP_TASKS[chat_id] = {'running': True, 'workers': []}
    for bot_app in ALL_BOT_APPS:
        task = asyncio.create_task(pfp_worker(bot_app, chat_id, [path], chat_id))
        PFP_TASKS[chat_id]['workers'].append(task)
    await update.message.reply_text(mf("🖼️ PFP Loop Started!\n🛑 /stoppfp"))

async def b_stoppfp(update, context):
    if not is_admin(update.effective_user.id): await update.message.reply_text(UNAUTH); return
    chat_id = update.effective_chat.id
    if chat_id in PFP_TASKS and PFP_TASKS[chat_id]['running']:
        PFP_TASKS[chat_id]['running'] = False; await asyncio.sleep(1)
        for w in PFP_TASKS[chat_id].get('workers', []): w.cancel()
        del PFP_TASKS[chat_id]; await update.message.reply_text(mf("✅ PFP Stopped!"))
    else: await update.message.reply_text(mf("ℹ️ No Active PFP."))


# ═══════════════ 𝐓𝐎𝐎𝐋𝐒 ═══════════════
async def b_delay(update, context):
    if not is_admin(update.effective_user.id): await update.message.reply_text(UNAUTH); return
    if not context.args:
        await update.message.reply_text(mf(f"📌 /delay <sec>\nCurrent: {CHAT_DELAYS.get(update.effective_chat.id, 0)}s")); return
    try:
        d = max(0, float(context.args[0]))
    except:
        await update.message.reply_text(mf("❌ Invalid delay!")); return
    CHAT_DELAYS[update.effective_chat.id] = d
    await update.message.reply_text(mf(f"⏱️ Delay: {d}s"))

async def b_threads(update, context):
    if not is_admin(update.effective_user.id): await update.message.reply_text(UNAUTH); return
    if not context.args:
        await update.message.reply_text(mf(f"📌 /threads <1-10>\nCurrent: {CHAT_THREADS.get(update.effective_chat.id, 1)}")); return
    try:
        t = max(1, min(int(context.args[0]), 10))
    except:
        await update.message.reply_text(mf("❌ Invalid number!")); return
    CHAT_THREADS[update.effective_chat.id] = t
    await update.message.reply_text(mf(f"🧵 Threads: {t}"))

async def b_purge(update, context):
    if not is_admin(update.effective_user.id) or not update.message.reply_to_message: return
    parts = update.message.text.split()
    try:
        n = min(int(parts[1]) if len(parts)>1 else 100, 1000)
    except:
        n = 100
    rid = update.message.reply_to_message.message_id
    try: await update.message.delete()
    except: pass
    d = 0
    for mid in range(rid, rid+n):
        try: await context.bot.delete_message(update.effective_chat.id, mid); d += 1
        except: continue
        await asyncio.sleep(0.05)
    m = await context.bot.send_message(update.effective_chat.id, mf(f"🗑️ {d} Deleted!"))
    await auto_del(m)

async def b_purgeall(update, context):
    if not is_admin(update.effective_user.id): await update.message.reply_text(UNAUTH); return
    parts = update.message.text.split()
    try:
        n = min(int(parts[1]) if len(parts)>1 else 100, 1000)
    except:
        n = 100
    try: await update.message.delete()
    except: pass
    d = 0
    async for msg in context.bot.get_chat_history(update.effective_chat.id, limit=n):
        try: await msg.delete(); d += 1
        except: continue
        await asyncio.sleep(0.05)
    m = await context.bot.send_message(update.effective_chat.id, mf(f"🗑️ {d} Deleted!"))
    await auto_del(m)

async def b_lock(update, context):
    if not is_admin(update.effective_user.id): await update.message.reply_text(UNAUTH); return
    no = ChatPermissions(can_send_messages=False, can_send_polls=False, can_send_other_messages=False,
                          can_add_web_page_previews=False, can_change_info=False, can_invite_users=False, can_pin_messages=False)
    done = 0
    for bot_app in ALL_BOT_APPS:
        try:
            await bot_app.bot.set_chat_permissions(update.effective_chat.id, no)
            done += 1
        except: continue
    if done > 0:
        await update.message.reply_text(mf(f"🔒 Locked! ({done} bots)"))
    else:
        await update.message.reply_text(mf("❌ Failed!"))

async def b_unlock(update, context):
    if not is_admin(update.effective_user.id): await update.message.reply_text(UNAUTH); return
    allp = ChatPermissions(can_send_messages=True, can_send_polls=True, can_send_other_messages=True,
                            can_add_web_page_previews=True, can_change_info=False, can_invite_users=True, can_pin_messages=False)
    done = 0
    for bot_app in ALL_BOT_APPS:
        try:
            await bot_app.bot.set_chat_permissions(update.effective_chat.id, allp)
            done += 1
        except: continue
    if done > 0:
        await update.message.reply_text(mf(f"🔓 Unlocked! ({done} bots)"))
    else:
        await update.message.reply_text(mf("❌ Failed!"))

async def b_adminoff(update, context):
    if not is_admin(update.effective_user.id): await update.message.reply_text(UNAUTH); return
    chat_id = update.effective_chat.id; count = 0
    for bot_app in ALL_BOT_APPS:
        try:
            bot = await bot_app.bot.get_me()
            await context.bot.promote_chat_member(chat_id, bot.id, can_change_info=False,
                can_delete_messages=False, can_invite_users=False,
                can_restrict_members=False, can_pin_messages=False, can_promote_members=False,
                can_manage_video_chats=False, can_manage_chat=False)
            count += 1
        except: pass
    await update.message.reply_text(mf(f"✅ {count} Bots Demoted!"))

async def b_leave(update, context):
    if not is_admin(update.effective_user.id): await update.message.reply_text(UNAUTH); return
    bot = await context.bot.get_me()
    await update.message.reply_text(mf(f"🚪 @{bot.username} Leaving...\n👤 Tera Account SAFE!"))
    await asyncio.sleep(2)
    try: await context.bot.leave_chat(update.effective_chat.id)
    except: pass

async def b_leaveall(update, context):
    if not is_admin(update.effective_user.id): await update.message.reply_text(UNAUTH); return
    chat_id = update.effective_chat.id
    await update.message.reply_text(mf("🚪 All Bots Leaving..."))
    for bot_app in ALL_BOT_APPS:
        try: await bot_app.bot.leave_chat(chat_id); await asyncio.sleep(0.2)
        except: pass

async def b_stopall(update, context):
    if not is_admin(update.effective_user.id): await update.message.reply_text(UNAUTH); return
    chat_id = update.effective_chat.id; stopped = []
    
    task_dicts = [
        ("NC", NC_TASKS), ("Spam", SPAM_TASKS), ("RSPAM", RSPAM_TASKS),
        ("Reply", REPLY_TASKS), ("RR", RR_TASKS), ("Emoji", EMOJI_TASKS),
        ("TTS Spam", TTSSPAM_TASKS), ("PicSpam", PICSPAM_TASKS), ("PFP", PFP_TASKS)
    ]
    
    for name, tasks in task_dicts:
        if chat_id in tasks and tasks[chat_id].get('running', False):
            tasks[chat_id]['running'] = False
            await asyncio.sleep(0.3)
            for w in tasks[chat_id].get('workers', []):
                w.cancel()
            del tasks[chat_id]
            stopped.append(name)
    
    for d in [PENDING_REPLIES, PENDING_RR]:
        if chat_id in d: del d[chat_id]
    if chat_id in RR_TARGETS: del RR_TARGETS[chat_id]
    if chat_id in RSPAM_TARGETS: del RSPAM_TARGETS[chat_id]
    
    await update.message.reply_text(mf(f"✅ Stopped: {', '.join(stopped)}") if stopped else mf("ℹ️ Nothing Active"))


# ═══════════════ 𝐒𝐓𝐀𝐓𝐔𝐒 ═══════════════
async def b_status(update, context):
    uptime_secs = int(time.time() - GLOBAL_STATS["start_time"])
    h, rem = divmod(uptime_secs, 3600); m, s = divmod(rem, 60); d, h = divmod(h, 24)
    parts = []
    if d: parts.append(f"{d}d")
    if h: parts.append(f"{h}h")
    if m: parts.append(f"{m}m")
    parts.append(f"{s}s")
    
    await update.message.reply_text(
        mf(
            f"📊 STATUS\n"
            f"⏱️ Uptime: {' '.join(parts)}\n"
            f"🤖 Bots: {len(ALL_BOT_APPS)}\n"
            f"💬 Messages: {GLOBAL_STATS['messages_sent']}\n"
            f"🔄 NC: {GLOBAL_STATS['name_changes']}\n"
            f"↩️ Replies: {GLOBAL_STATS['replies_sent']}\n"
            f"💣 RSPAM: {GLOBAL_STATS['rspam_sent']}"
        )
    )

async def b_uptime(update, context):
    uptime_secs = int(time.time() - GLOBAL_STATS["start_time"])
    h, rem = divmod(uptime_secs, 3600); m, s = divmod(rem, 60); d, h = divmod(h, 24)
    parts = []
    if d: parts.append(f"{d}d")
    if h: parts.append(f"{h}h")
    if m: parts.append(f"{m}m")
    parts.append(f"{s}s")
    await update.message.reply_text(mf(f"⏱️ Uptime: {' '.join(parts)}\n🤖 Bots: {len(ALL_BOT_APPS)}"))

async def b_react(update, context):
    chat_id = update.effective_chat.id
    if chat_id in REACT_CHATS:
        del REACT_CHATS[chat_id]; await update.message.reply_text(mf("✅ React OFF"))
    else:
        REACT_CHATS[chat_id] = True; REACT_EMOJI[chat_id] = "🤣"
        await update.message.reply_text(mf("✅ React ON (🤣)"))

async def b_ereact(update, context):
    if not context.args: await update.message.reply_text(mf("📌 /ereact <emoji>")); return
    chat_id = update.effective_chat.id; emoji = context.args[0]
    REACT_CHATS[chat_id] = True; REACT_EMOJI[chat_id] = emoji
    await update.message.reply_text(mf(f"✅ React ON ({emoji})"))


# ═══════════════ 𝐒𝐓𝐀𝐓𝐔𝐒 𝐇𝐀𝐍𝐃𝐋𝐄𝐑 ═══════════════
async def status_handler(update, context):
    if not update.my_chat_member: return
    chat = update.my_chat_member.chat
    old = update.my_chat_member.old_chat_member.status
    new = update.my_chat_member.new_chat_member.status
    bot = await context.bot.get_me()
    
    if new in ["left", "kicked"] and old in ["member", "administrator"]:
        action = "KICKED" if new == "kicked" else "LEFT"
        try:
            await context.bot.send_message(OWNER_ID, mf(f"🚨 Bot {action}!\n🤖 @{bot.username}\n📛 {chat.title}\n🆔 {chat.id}"))
        except: pass
    elif new == "member" and old not in ["member", "administrator"]:
        try:
            await context.bot.send_message(OWNER_ID, mf(f"✅ Bot Added!\n🤖 @{bot.username}\n📛 {chat.title}\n🆔 {chat.id}"))
        except: pass


# ═══════════════ 𝐌𝐄𝐒𝐒𝐀𝐆𝐄 𝐂𝐎𝐋𝐋𝐄𝐂𝐓𝐎𝐑 ═══════════════
async def msg_collector(update, context):
    if not update.message: return
    chat_id = update.effective_chat.id; msg_id = update.message.message_id
    
    if chat_id in REACT_CHATS:
        try: await update.message.set_reaction(reaction=REACT_EMOJI.get(chat_id, "🤣"))
        except: pass
    
    if not update.message.text: return
    sender = update.message.from_user
    sender_id = sender.id if sender else None
    
    if chat_id in REPLY_TASKS and REPLY_TASKS[chat_id].get('running'):
        if chat_id not in PENDING_REPLIES: PENDING_REPLIES[chat_id] = []
        PENDING_REPLIES[chat_id].append(msg_id)
    
    if chat_id in RR_TASKS and RR_TASKS[chat_id].get('running'):
        if sender_id and sender_id == RR_TARGETS.get(chat_id):
            if chat_id not in PENDING_RR: PENDING_RR[chat_id] = []
            PENDING_RR[chat_id].append(msg_id)


# ═══════════════ 𝐇𝐎𝐒𝐓𝐄𝐃 𝐁𝐎𝐓 𝐇𝐄𝐋𝐏𝐄𝐑 ═══════════════
def add_all_handlers(app):
    """Add all command handlers to a bot app"""
    app.add_handler(CommandHandler("start", b_start))
    app.add_handler(CommandHandler("menu", b_menu))
    app.add_handler(CommandHandler("ping", b_ping))
    app.add_handler(CommandHandler("music", b_music))
    app.add_handler(CommandHandler("find", b_find))
    app.add_handler(CommandHandler("tts", b_tts))
    app.add_handler(CommandHandler("ttsja", b_ttsja))
    app.add_handler(CommandHandler("ttsspam", b_ttsspam))
    app.add_handler(CommandHandler("ttsspamja", b_ttsspamja))
    app.add_handler(CommandHandler("stopttsspam", b_stopttsspam))
    app.add_handler(CommandHandler("mute", b_mute))
    app.add_handler(CommandHandler("unmute", b_unmute))
    app.add_handler(CommandHandler("changename", b_changename))
    app.add_handler(CommandHandler("changebio", b_changebio))
    app.add_handler(CommandHandler("changepfp", b_changepfp))
    app.add_handler(CommandHandler("admin", b_admin))
    app.add_handler(CommandHandler("legarib", b_legarib))
    app.add_handler(CommandHandler("hatgarib", b_hatgarib))
    app.add_handler(CommandHandler("garibokilist", b_garibokilist))
    app.add_handler(CommandHandler("addhost", b_addhost))
    app.add_handler(CommandHandler("mybots", b_mybots))
    app.add_handler(CommandHandler("removehost", b_removehost))
    app.add_handler(CommandHandler("hostlist", b_hostlist))
    app.add_handler(CommandHandler("nc", b_nc))
    app.add_handler(CommandHandler("nc2", b_nc2))
    app.add_handler(CommandHandler("nc3", b_nc3))
    app.add_handler(CommandHandler("sylasnc", b_sylasnc))
    app.add_handler(CommandHandler("sylasnc2", b_sylasnc2))
    app.add_handler(CommandHandler("tridentnc", b_tridentnc))
    app.add_handler(CommandHandler("sync", b_sync))
    app.add_handler(CommandHandler("stopnc", b_stopnc))
    app.add_handler(CommandHandler("spam", b_spam))
    app.add_handler(CommandHandler("stopspam", b_stopspam))
    app.add_handler(CommandHandler("rspam", b_rspam))
    app.add_handler(CommandHandler("stoprspam", b_stoprspam))
    app.add_handler(CommandHandler("emojis", b_emojis))
    app.add_handler(CommandHandler("stopemojis", b_stopemojis))
    app.add_handler(CommandHandler("reply", b_reply))
    app.add_handler(CommandHandler("stopreply", b_stopreply))
    app.add_handler(CommandHandler("rr", b_rr))
    app.add_handler(CommandHandler("stoprr", b_stoprr))
    app.add_handler(CommandHandler("picspam", b_picspam))
    app.add_handler(CommandHandler("stoppicspam", b_stoppicspam))
    app.add_handler(CommandHandler("pfp", b_pfp))
    app.add_handler(CommandHandler("stoppfp", b_stoppfp))
    app.add_handler(CommandHandler("delay", b_delay))
    app.add_handler(CommandHandler("threads", b_threads))
    app.add_handler(CommandHandler("purge", b_purge))
    app.add_handler(CommandHandler("purgeall", b_purgeall))
    app.add_handler(CommandHandler("lock", b_lock))
    app.add_handler(CommandHandler("unlock", b_unlock))
    app.add_handler(CommandHandler("adminoff", b_adminoff))
    app.add_handler(CommandHandler("leave", b_leave))
    app.add_handler(CommandHandler("leaveall", b_leaveall))
    app.add_handler(CommandHandler("stopall", b_stopall))
    app.add_handler(CommandHandler("uptime", b_uptime))
    app.add_handler(CommandHandler("status", b_status))
    app.add_handler(CommandHandler("react", b_react))
    app.add_handler(CommandHandler("ereact", b_ereact))


async def run_hosted_bot(token, bot_num):
    """Run a hosted bot for sudo users"""
    await asyncio.sleep(1)
    while True:
        app = Application.builder().token(token).build()
        add_all_handlers(app)
        try:
            await app.initialize(); await app.start()
            await app.updater.start_polling(drop_pending_updates=True)
            bot = await app.bot.get_me()
            print(f"  🌐 Hosted Bot {bot_num}: @{bot.username}")
            HOSTED_APPS.append(app); ALL_BOT_APPS.append(app)
            while True: await asyncio.sleep(3600)
        except TelegramConflict:
            try: await app.updater.stop(); await app.stop(); await app.shutdown()
            except: pass
            await asyncio.sleep(5); continue
        except Exception as e: print(f"  ❌ Hosted Bot {bot_num}: {e}"); break
        finally:
            if app in HOSTED_APPS: HOSTED_APPS.remove(app)
            if app in ALL_BOT_APPS: ALL_BOT_APPS.remove(app)
            try: await app.updater.stop(); await app.stop(); await app.shutdown()
            except: pass
        break


# ═══════════════ 𝐁𝐎𝐓 𝐅𝐀𝐂𝐓𝐎𝐑𝐘 ═══════════════
def create_bot_app(token):
    app = Application.builder().token(token).build()
    add_all_handlers(app)
    
    # ═══════════ 𝐏𝐑𝐄𝐅𝐈𝐗 𝐇𝐀𝐍𝐃𝐋𝐄𝐑 (. !) ═══════════
    async def prefix_handler(update, context):
        if not update.message or not update.message.text: return
        text = update.message.text
        prefix = text[0] if text else ""
        if prefix in ['.', '!']:
            parts = text[1:].split()
            if not parts: return
            command = parts[0].lower(); context.args = parts[1:]
            cmd_map = {
                "ping": b_ping, "menu": b_menu, "music": b_music, "find": b_find,
                "tts": b_tts, "ttsja": b_ttsja, "ttsspam": b_ttsspam, "ttsspamja": b_ttsspamja, "stopttsspam": b_stopttsspam,
                "mute": b_mute, "unmute": b_unmute,
                "changename": b_changename, "changebio": b_changebio, "changepfp": b_changepfp,
                "admin": b_admin, "adminoff": b_adminoff,
                "legarib": b_legarib, "hatgarib": b_hatgarib, "garibokilist": b_garibokilist,
                "addhost": b_addhost, "mybots": b_mybots, "removehost": b_removehost, "hostlist": b_hostlist,
                "nc": b_nc, "nc2": b_nc2, "nc3": b_nc3, "sylasnc": b_sylasnc, "sylasnc2": b_sylasnc2,
                "tridentnc": b_tridentnc, "sync": b_sync, "stopnc": b_stopnc,
                "spam": b_spam, "stopspam": b_stopspam, "rspam": b_rspam, "stoprspam": b_stoprspam,
                "emojis": b_emojis, "stopemojis": b_stopemojis,
                "reply": b_reply, "stopreply": b_stopreply, "rr": b_rr, "stoprr": b_stoprr,
                "picspam": b_picspam, "stoppicspam": b_stoppicspam, "pfp": b_pfp, "stoppfp": b_stoppfp,
                "delay": b_delay, "threads": b_threads, "purge": b_purge, "purgeall": b_purgeall,
                "lock": b_lock, "unlock": b_unlock, "leave": b_leave, "leaveall": b_leaveall,
                "stopall": b_stopall, "uptime": b_uptime, "status": b_status,
                "react": b_react, "ereact": b_ereact, "start": b_start,
            }
            if command in cmd_map: await cmd_map[command](update, context)
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, prefix_handler))
    app.add_handler(ChatMemberHandler(status_handler, ChatMemberHandler.MY_CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, msg_collector))
    
    return app


# ═══════════════ 𝐁𝐎𝐓 𝐑𝐔𝐍𝐍𝐄𝐑 ═══════════════
async def run_single_bot(token, bot_num):
    await asyncio.sleep(bot_num * 3)
    proxy_url = get_proxy(bot_num)
    request = HTTPXRequest(proxy_url=proxy_url) if proxy_url else None
    
    while True:
        builder = Application.builder().token(token)
        if request: builder.request(request)
        app = builder.build()
        add_all_handlers(app)
        
        async def prefix_handler(update, context):
            if not update.message or not update.message.text: return
            text = update.message.text
            prefix = text[0] if text else ""
            if prefix in ['.', '!']:
                parts = text[1:].split()
                if not parts: return
                command = parts[0].lower(); context.args = parts[1:]
                cmd_map = {
                    "ping": b_ping, "menu": b_menu, "music": b_music, "find": b_find,
                    "tts": b_tts, "ttsja": b_ttsja, "ttsspam": b_ttsspam, "ttsspamja": b_ttsspamja, "stopttsspam": b_stopttsspam,
                    "mute": b_mute, "unmute": b_unmute,
                    "changename": b_changename, "changebio": b_changebio, "changepfp": b_changepfp,
                    "admin": b_admin, "adminoff": b_adminoff,
                    "legarib": b_legarib, "hatgarib": b_hatgarib, "garibokilist": b_garibokilist,
                    "addhost": b_addhost, "mybots": b_mybots, "removehost": b_removehost, "hostlist": b_hostlist,
                    "nc": b_nc, "nc2": b_nc2, "nc3": b_nc3, "sylasnc": b_sylasnc, "sylasnc2": b_sylasnc2,
                    "tridentnc": b_tridentnc, "sync": b_sync, "stopnc": b_stopnc,
                    "spam": b_spam, "stopspam": b_stopspam, "rspam": b_rspam, "stoprspam": b_stoprspam,
                    "emojis": b_emojis, "stopemojis": b_stopemojis,
                    "reply": b_reply, "stopreply": b_stopreply, "rr": b_rr, "stoprr": b_stoprr,
                    "picspam": b_picspam, "stoppicspam": b_stoppicspam, "pfp": b_pfp, "stoppfp": b_stoppfp,
                    "delay": b_delay, "threads": b_threads, "purge": b_purge, "purgeall": b_purgeall,
                    "lock": b_lock, "unlock": b_unlock, "leave": b_leave, "leaveall": b_leaveall,
                    "stopall": b_stopall, "uptime": b_uptime, "status": b_status,
                    "react": b_react, "ereact": b_ereact, "start": b_start,
                }
                if command in cmd_map: await cmd_map[command](update, context)
        
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, prefix_handler))
        app.add_handler(ChatMemberHandler(status_handler, ChatMemberHandler.MY_CHAT_MEMBER))
        app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, msg_collector))
        
        try:
            await app.initialize()
            await app.start()
            await app.updater.start_polling(drop_pending_updates=True)
            bot = await app.bot.get_me()
            proxy_info = f" [Proxy]" if proxy_url else ""
            print(f"  ✅ Bot {bot_num}: @{bot.username}{proxy_info}")
            ALL_BOT_APPS.append(app)
            while True: await asyncio.sleep(3600)
        except TelegramConflict:
            try: await app.updater.stop(); await app.stop(); await app.shutdown()
            except: pass
            await asyncio.sleep(5); continue
        except Exception as e:
            if "flood" in str(e).lower():
                m = re.search(r'retry in (\d+)', str(e).lower())
                try: await app.updater.stop(); await app.stop(); await app.shutdown()
                except: pass
                if m:
                    await asyncio.sleep(int(m.group(1)) + 2)
                else:
                    await asyncio.sleep(30)
                continue
            print(f"  ❌ Bot {bot_num}: {e}"); break
        finally:
            if app in ALL_BOT_APPS: ALL_BOT_APPS.remove(app)
            try: await app.updater.stop(); await app.stop(); await app.shutdown()
            except: pass
        break


# ═══════════════ 𝐌𝐀𝐈𝐍 ═══════════════
async def main():
    print(mf("🤖 SYLAS HYBRID - SUPREME NC\n"))
    
    asyncio.create_task(keepalive_server())
    
    # Load and start hosted bots
    for uid, bots in HOSTED_BOTS.items():
        for bot in bots:
            asyncio.create_task(run_hosted_bot(bot['token'], bot['bot_num']))
    
    session = await get_session()
    print(mf("📱 Userbot..."))
    ub = TelegramClient(StringSession(session), API_ID, API_HASH)
    ub.add_event_handler(ub_bots)
    await ub.start()
    print(f"  ✅ {(await ub.get_me()).first_name}\n")
    print(mf(f"🤖 {len(BOT_TOKENS)} Bots..."))
    bot_tasks = [asyncio.create_task(run_single_bot(t, i)) for i, t in enumerate(BOT_TOKENS, 1)]
    print(mf("✅ READY! .menu /menu !menu Sab Chalega!\n"))
    try: await asyncio.gather(*bot_tasks)
    except KeyboardInterrupt: pass
    print(mf("\n🛑 Done."))
    await ub.disconnect()


if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: print("\n👋")