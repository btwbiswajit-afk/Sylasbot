"""
╭────────────── 𓂃𓈒𓏸 ──────────────╮
              𝑆ʏ𝐿ᴀs  𝑮ᴏᴅ  𝑀ᴏᴅ  v7.0
╰────────────── 𓂃𓈒𓏸 ──────────────╯
"""

import asyncio
import os
import sys
import pathlib
import tempfile
import time
import random
import re
import json
import logging
from logging.handlers import RotatingFileHandler

try:
    import uvloop
    uvloop.install()
except Exception:
    pass

import yt_dlp
from aiohttp import web
from gtts import gTTS
import edge_tts
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.channels import InviteToChannelRequest, EditAdminRequest
from telethon.tl.functions.messages import AddChatUserRequest
from telethon.tl.types import ChatAdminRights
from telethon.errors import SessionPasswordNeededError
from telegram import (
    Update, Bot, ChatPermissions,
    InlineKeyboardButton, InlineKeyboardMarkup,
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ChatMemberHandler, CallbackQueryHandler,
    filters, ContextTypes,
)
from telegram.error import (
    TelegramError, Conflict as TelegramConflict,
    RetryAfter, TimedOut, NetworkError,
)
from telegram.request import HTTPXRequest

VERSION = "sylas~god~mod-7.0"

_STYLE_POOL = {
    "a": ["ᴀ", "𝐚", "ꪖ", "𝖺", "𝒂"], "b": ["ʙ", "𝐛", "𝖻", "𝒃", "𝗯"],
    "c": ["ᴄ", "𝐜", "𝖼", "𝒄", "𝗰"], "d": ["ᴅ", "𝐝", "𝖽", "𝒅", "𝗱"],
    "e": ["ᴇ", "𝐞", "𝖾", "𝒆", "𝗲"], "f": ["ꜰ", "𝐟", "𝖿", "𝒇", "𝗳"],
    "g": ["ɢ", "𝐠", "𝗀", "𝒈", "𝗴"], "h": ["ʜ", "𝐡", "𝗁", "𝒉", "𝗵"],
    "i": ["ɪ", "𝐢", "𝗂", "𝒊", "𝗶"], "j": ["ᴊ", "𝐣", "𝗃", "𝒋", "𝗷"],
    "k": ["ᴋ", "𝐤", "𝗄", "𝒌", "𝗸"], "l": ["ʟ", "𝐥", "𝗅", "𝒍", "𝗹"],
    "m": ["ᴍ", "𝐦", "𝗆", "𝒎", "𝗺"], "n": ["ɴ", "𝐧", "𝗇", "𝒏", "𝗻"],
    "o": ["ᴏ", "𝐨", "𝗈", "𝒐", "𝗼"], "p": ["ᴘ", "𝐩", "𝗉", "𝒑", "𝗽"],
    "q": ["ǫ", "𝐪", "𝗊", "𝒒", "𝗾"], "r": ["ʀ", "𝐫", "𝗋", "𝒓", "𝗿"],
    "s": ["s", "𝐬", "𝗌", "𝒔", "𝘀"], "t": ["ᴛ", "𝐭", "𝗍", "𝒕", "𝘁"],
    "u": ["ᴜ", "𝐮", "𝗎", "𝒖", "𝘂"], "v": ["ᴠ", "𝐯", "𝗏", "𝒗", "𝘃"],
    "w": ["ᴡ", "𝐰", "𝗐", "𝒘", "𝘄"], "x": ["x", "𝐱", "𝗑", "𝒙", "𝘅"],
    "y": ["ʏ", "𝐲", "𝗒", "𝒚", "𝘆"], "z": ["ᴢ", "𝐳", "𝗓", "𝒛", "𝘇"],
}

_STYLE_LOCK = {}

def _get_style(ch):
    if ch not in _STYLE_LOCK:
        _STYLE_LOCK[ch] = random.choice(_STYLE_POOL[ch])
    return _STYLE_LOCK[ch]

def mf(text):
    out = []
    for ch in text:
        low = ch.lower()
        if low in _STYLE_POOL:
            out.append(_get_style(low))
        else:
            out.append(ch)
    return "".join(out)

SYLAS_DISPLAY = "𝐒𝘆𝖑𝖆𝘴 ᛉ"
MADE_BY = mf("Made by ") + SYLAS_DISPLAY

def ast_box(title, body, emoji="⟡"):
    return (
        "╭────────────── 𓂃𓈒𓏸 ──────────────╮\n\n"
       f"        {emoji} " + mf(title) + "\n\n"
        "     ─────────────────────────\n\n"
       f"{body}\n\n"
        "╰────────────── 𓂃𓈒𓏸 ──────────────╯"
    )

def ast_ok(msg):   return ast_box("SYLAS DONE", "        " + mf(msg), "✅")
def ast_err(msg):  return ast_box("SYLAS ERROR", "        " + mf(msg), "⚠️")
def ast_info(msg): return ast_box("SYLAS INFO", "        " + mf(msg), "ℹ️")
def ast_warn(msg): return ast_box("SYLAS NOTICE", "        " + mf(msg), "🔱")

def short_ok(msg):   return "⟡ " + mf("SYLAS") + " · ✅ " + mf(msg)
def short_err(msg):  return "⟡ " + mf("SYLAS") + " · ⚠️ " + mf(msg)
def short_info(msg): return "⟡ " + mf("SYLAS") + " · ℹ️ " + mf(msg)
def short_warn(msg): return "⟡ " + mf("SYLAS") + " · 🔱 " + mf(msg)

def get_env(name, default=""):
    return os.getenv(name, default).strip()

logger = logging.getLogger("sylas")
logger.setLevel(logging.INFO)
try:
    _fh = RotatingFileHandler("sylas.log", maxBytes=5 * 1024 * 1024, backupCount=3)
    _fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(_fh)
except Exception:
    pass

API_ID = int(get_env("API_ID", "32070897"))
API_HASH = get_env("API_HASH", "445b591a8ce0d236a81f47b68a8f2a1d")
OWNER_ID = int(get_env("OWNER_ID", "8663186943"))

BOT_TOKENS = []
_tokens_file = pathlib.Path("tokens.json")
if _tokens_file.exists():
    try:
        _data = json.loads(_tokens_file.read_text())
        if isinstance(_data, list):
            BOT_TOKENS = [t.strip() for t in _data if isinstance(t, str) and t.strip()]
        elif isinstance(_data, dict):
            BOT_TOKENS = [v.strip() for v in _data.values() if isinstance(v, str) and v.strip()]
    except Exception as e:
        print(f"⚠️ tokens.json parse failed: {e}")

if not BOT_TOKENS:
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

ADMIN_IDS = {OWNER_ID}
AUTO_DEL = 5
MAX_AUDIO_MB = 50
PREFIXES = ("/", ".", "!", "~")

NC_DELAY = 0
SPAM_DELAY = 0
SEMAPHORE_PER_BOT = 20
RETRY_AFTER_BUFFER = 0.3
BATCH_SIZE = 10
BATCH_DELAY = 0.3
POOL_SIZE = 1024
CONNECT_TIMEOUT = 10
READ_TIMEOUT = 30
REPLY_LOCK_TTL = 0.5
MIN_NC_INTERVAL = 0.05

UNSUDO_MSG = "𝐴ꪗ𝑦𝑦 ꪑᴀ𝐃ᴀʀCᴏᴪ 𝐀ᑭꪀꪖ Kᴀꪑ Kᴀ᥅ɴᴀ"

BOT_WELCOME = (
    "╭────────────── 𓂃𓈒𓏸 ──────────────╮\n\n"
    "              " + SYLAS_DISPLAY + "\n\n"
    "        " + mf('"beyond the ordinary"') + "\n\n"
    "     ─────────────────────────\n\n"
    "        " + mf("SYSTEM") + "  ·  " + mf("ONLINE") + "\n\n"
    "     ─────────────────────────\n\n"
    "        " + mf("WHAT I DO") + "\n\n"
    "        ⟡ " + mf("Group Management") + "\n"
    "        ⟡ " + mf("Reply and RR") + "\n"
    "        ⟡ " + mf("Music and TTS") + "\n"
    "        ⟡ " + mf("NC and Sync") + "\n"
    "        ⟡ " + mf("Spam and Flood") + "\n"
    "        ⟡ " + mf("Hosting and Sudo") + "\n\n"
    "     ─────────────────────────\n\n"
    "        " + MADE_BY + "\n\n"
    "        " + mf("Your Status") + "\n"
    "        {status}\n\n"
    "        " + mf("Type") + " /menu " + mf("to begin") + "\n\n"
    "╰────────────── 𓂃𓈒𓏸 ──────────────╯"
)
# ═══════════════ 𝐑𝐄𝐏𝐋𝐘 𝐋𝐎𝐂𝐊 ═══════════════
CMD_REPLY_LOCK = {}

def acquire_reply_lock(cmd, chat_id):
    key = f"{cmd}:{chat_id}"
    now = time.time()
    if key in CMD_REPLY_LOCK and now - CMD_REPLY_LOCK[key] < REPLY_LOCK_TTL:
        return False
    CMD_REPLY_LOCK[key] = now
    if len(CMD_REPLY_LOCK) > 5000:
        cutoff = now - 60
        for k in list(CMD_REPLY_LOCK.keys()):
            if CMD_REPLY_LOCK[k] < cutoff:
                del CMD_REPLY_LOCK[k]
    return True

# ═══════════════ 𝐒𝐄𝐌𝐀𝐏𝐇𝐎𝐑𝐄 ═══════════════
BOT_SEMAPHORES = {}

def get_sem(bot_id):
    if bot_id not in BOT_SEMAPHORES:
        BOT_SEMAPHORES[bot_id] = asyncio.Semaphore(SEMAPHORE_PER_BOT)
    return BOT_SEMAPHORES[bot_id]

# ═══════════════ 𝐒𝐄𝐒𝐒𝐈𝐎𝐍 ═══════════════
SESSION_FILE_NAME = "session_string.txt"
HOME_DIR = pathlib.Path.home()
SESSION_PATHS = [
    pathlib.Path.cwd() / SESSION_FILE_NAME,
    HOME_DIR / ".sylas" / SESSION_FILE_NAME,
    HOME_DIR / ".config" / "sylas" / SESSION_FILE_NAME,
    pathlib.Path("/tmp/sylas") / SESSION_FILE_NAME,
]

def _atomic_write(path, data):
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        with open(tmp, "w") as f:
            f.write(data)
        try:
            os.chmod(tmp, 0o600)
        except Exception:
            pass
        os.replace(tmp, path)
        return True
    except Exception as e:
        logger.warning(f"Session write failed {path}: {e}")
        return False

def save_session(ss):
    saved = 0
    for p in SESSION_PATHS:
        if _atomic_write(p, ss):
            saved += 1
    if saved:
        print(short_ok(f"Session saved · {saved} locations"))
    else:
        print(short_err("Session save failed everywhere"))

async def create_session():
    print(mf("\nFIRST TIME LOGIN"))
    phone = input(mf("Phone (+countrycode): ")).strip()
    client = TelegramClient(StringSession(), API_ID, API_HASH)
    await client.connect()
    try:
        sent = await client.send_code_request(phone)
        code = input(mf("OTP: ")).strip()
        try:
            await client.sign_in(phone=phone, code=code, phone_code_hash=sent.phone_code_hash)
        except SessionPasswordNeededError:
            pw = input(mf("2FA Password: ")).strip()
            await client.sign_in(password=pw)
        ss = client.session.save()
        save_session(ss)
        print(short_ok("Session saved · ab dobara login nahi maangega"))
        print(mf("SESSION_STRING (backup rakh le):"))
        print(ss)
        print()
        await client.disconnect()
        return ss
    except Exception as e:
        print(short_err(f"Login failed · {e}"))
        try:
            await client.disconnect()
        except Exception:
            pass
        sys.exit(1)

async def get_session():
    candidates = []
    env = os.getenv("SESSION_STRING", "").strip()
    if env:
        candidates.append(("env", env))
    for p in SESSION_PATHS:
        try:
            if p.exists():
                data = p.read_text().strip()
                if data:
                    candidates.append((str(p), data))
        except Exception:
            continue
    for src, ss in candidates:
        try:
            c = TelegramClient(StringSession(ss), API_ID, API_HASH)
            await c.connect()
            ok = await c.is_user_authorized()
            await c.disconnect()
            if ok:
                print(short_ok(f"Session OK · {src}"))
                save_session(ss)
                return ss
            else:
                print(short_warn(f"Unauthorized · {src}"))
        except Exception as e:
            print(short_warn(f"Session check failed · {src} · {e}"))
    return await create_session()

# ═══════════════ 𝐏𝐑𝐎𝐗𝐘 ═══════════════
PROXY_LIST = []
if os.path.exists("proxies.txt"):
    try:
        with open("proxies.txt") as f:
            PROXY_LIST = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(short_err(f"proxies.txt read failed · {e}"))
else:
    print(short_info("proxies.txt not found — running direct"))

def get_proxy(bot_num):
    if PROXY_LIST:
        return PROXY_LIST[(bot_num - 1) % len(PROXY_LIST)]
    return None

# ═══════════════ 𝐆𝐋𝐎𝐁𝐀𝐋 𝐒𝐓𝐀𝐓𝐒 ═══════════════
GLOBAL_STATS = {
    "messages_sent": 0,
    "replies_sent": 0,
    "start_time": time.time(),
}

# ═══════════════ 𝐓𝐀𝐒𝐊 𝐃𝐈𝐂𝐓𝐒 ═══════════════
REPLY_TASKS = {}
RR_TASKS = {}
PENDING_REPLIES = {}
PENDING_RR = {}
RR_TARGETS = {}
CHAT_DELAYS = {}
REACT_CHATS = {}
REACT_EMOJI = {}
REACT_MODE = {}
REACT_ALL_POOL = ["🤣","🔥","💀","❤️","👏","🎉","😍","⚡","👑","🖤","🤍","💯","🥰","😂","🤯","😎","💥","🌟","✨","💫"]
ALL_BOT_APPS = set()
PRIMARY_BOT_ID = None

# ═══════════════ 𝐏𝐈𝐂𝐒𝐏𝐀𝐌 / 𝐏𝐅𝐏 ═══════════════
PICSPAM_TASKS = {}
PICSPAM_MEDIA = {}
PFP_TASKS = {}
PFP_MEDIA = {}

# ═══════════════ 𝐇𝐎𝐒𝐓𝐈𝐍𝐆 ═══════════════
HOSTED_BOTS_FILE = "hosted_bots.json"
HOSTED_BOTS = {}
HOSTED_APPS = set()
HOSTED_BOT_COUNTER = 0

def load_hosted_bots():
    global HOSTED_BOTS
    if os.path.exists(HOSTED_BOTS_FILE):
        try:
            with open(HOSTED_BOTS_FILE) as f:
                HOSTED_BOTS = json.load(f)
        except Exception:
            HOSTED_BOTS = {}
    else:
        HOSTED_BOTS = {}

def save_hosted_bots():
    try:
        tmp = HOSTED_BOTS_FILE + ".tmp"
        with open(tmp, "w") as f:
            json.dump(HOSTED_BOTS, f)
        os.replace(tmp, HOSTED_BOTS_FILE)
    except Exception as e:
        logger.warning(f"save_hosted_bots failed: {e}")

load_hosted_bots()

# ═══════════════ 𝐇𝐄𝐋𝐏𝐄𝐑𝐒 ═══════════════
def is_admin(uid):
    return uid in ADMIN_IDS

async def safe_edit(m, t):
    try:
        await m.edit_text(t)
    except Exception:
        pass

async def auto_del(m, d=AUTO_DEL):
    try:
        await asyncio.sleep(d)
        await m.delete()
    except Exception:
        pass

async def get_bot_usernames():
    u = []
    for t in BOT_TOKENS:
        try:
            b = Bot(t)
            i = await b.get_me()
            u.append(i.username)
            await b.close()
        except Exception:
            pass
    return u

def pick_target(update, context, default="Chutiya"):
    if update.message.reply_to_message and update.message.reply_to_message.from_user:
        return update.message.reply_to_message.from_user.first_name
    if context.args:
        return " ".join(context.args)
    return default

async def _parallel_bot_op(op_name, coro_factory):
    results = {"ok": 0, "fail": 0}
    lock = asyncio.Lock()

    async def wrap(bot_app):
        sem = get_sem(id(bot_app))
        async with sem:
            try:
                await coro_factory(bot_app)
                async with lock:
                    results["ok"] += 1
            except Exception:
                async with lock:
                    results["fail"] += 1

    await asyncio.gather(*[wrap(b) for b in list(ALL_BOT_APPS)])
    return results

# ═══════════════ 𝐌𝐄𝐍𝐔 (Fancy Box) ═══════════════
def build_menu(bot_username, status):
    return (
        "╭────────────── 𓂃𓈒𓏸 ──────────────╮\n\n"
        "              " + SYLAS_DISPLAY + "\n\n"
        "        " + mf('"beyond the ordinary"') + "\n\n"
        "     ─────────────────────────\n\n"
       f"        🤖 @{bot_username}\n"
        "        " + mf("STATUS") + " ·  " + status + "\n\n"
        "     ─────────────────────────\n\n"
        "        " + mf("EXPLORE SYLAS") + "\n\n"
        "        ⟡ " + mf("INTELLIGENCE") + "\n"
        "          › /ping  /menu  /status  /uptime\n\n"
        "        ⟡ " + mf("MEDIA") + "\n"
        "          › /tts  /ttsja  /changepfp\n\n"
        "        ⟡ " + mf("MUSIC") + "\n"
        "          › /music  /find\n\n"
        "        ⟡ " + mf("NC") + "\n"
        "          › /nc  /nc1  /sylasnc  /sync  /botnc\n"
        "          › /gnc  /lnc  /rnc  /sylasnc2\n"
        "          › /stopnc  /stopnc1  /stopsylasnc  /stopsync\n"
        "          › /stopbotnc  /stopgnc  /stoplnc  /stoprnc\n"
        "          › /stopsylasnc2\n\n"
        "        ⟡ " + mf("SPAM") + "\n"
        "          › /spam  /spam1  /dspam  /picspam\n"
        "          › /stopspam  /stopspam1  /stopdspam\n"
        "          › /stoppicspam\n\n"
        "        ⟡ " + mf("PFP") + "\n"
        "          › /pfp  /stoppfp\n\n"
        "        ⟡ " + mf("TOOLS") + "\n"
        "          › /lock  /unlock  /purge  /purgeall\n"
        "          › /delay  /react  /ereact\n"
        "          › /optimize  /stats\n\n"
        "        ⟡ " + mf("PROFILE") + "\n"
        "          › /changename  /changebio\n\n"
        "        ⟡ " + mf("ADMIN") + "\n"
        "          › /admin  /adminoff  /mute  /unmute\n\n"
        "        ⟡ " + mf("REPLY") + "\n"
        "          › /reply  /stopreply  /rr  /stoprr\n\n"
        "        ⟡ " + mf("HOSTING") + "\n"
        "          › /addhost  /mybots  /removehost  /hostlist\n\n"
        "        ⟡ " + mf("SUDO") + "\n"
        "          › /legarib  /hatgarib  /garibokilist\n\n"
        "        ⟡ " + mf("CONTROL") + "\n"
        "          › /stopall  /leave  /leaveall\n\n"
        "     ─────────────────────────\n\n"
        "          " + mf("Prefixes") + " : /  .  !  ~\n\n"
        "          " + SYLAS_DISPLAY + "\n"
        "        " + MADE_BY + "\n\n"
        "╰────────────── 𓂃𓈒𓏸 ──────────────╯"
    )


# ═══════════════ 𝐔𝐒𝐄𝐑𝐁𝐎𝐓 /𝐛𝐨𝐭𝐬 ═══════════════
@events.register(events.NewMessage(pattern="^/bots$"))
async def ub_bots(event):
    if not event.is_group:
        return
    if not is_admin(event.sender_id):
        await auto_del(await event.reply(UNSUDO_MSG))
        return
    group = await event.get_chat()
    is_sg = hasattr(group, 'megagroup') or hasattr(group, 'broadcast')
    if is_sg:
        me = await event.client.get_me()
        try:
            perm = await event.client.get_permissions(group, me)
            if not perm.is_admin:
                await event.reply(mf("Userbot Ko Admin Banao"))
                return
            if not perm.add_admins:
                await event.reply(mf("Add Admins Permission Do"))
                return
        except Exception:
            pass
    usernames = await get_bot_usernames()
    if not usernames:
        await event.reply(mf("No Valid Tokens"))
        return
    total = len(usernames)
    st = await event.reply(mf(f"Adding {total} Bots"))
    added, admin_ok, failed = 0, 0, 0
    entities = []
    for u in usernames:
        try:
            ent = await event.client.get_input_entity(u)
            entities.append((u, ent))
        except Exception:
            entities.append((u, u))

    for i in range(0, len(entities), BATCH_SIZE):
        batch = entities[i:i + BATCH_SIZE]
        add_tasks = []
        for u, ent in batch:
            if is_sg:
                add_tasks.append(event.client(InviteToChannelRequest(group, [ent])))
            else:
                add_tasks.append(event.client(AddChatUserRequest(chat_id=group.id, user_id=ent, fwd_limit=0)))
        results = await asyncio.gather(*add_tasks, return_exceptions=True)
        for r in results:
            if isinstance(r, Exception):
                failed += 1
            else:
                added += 1
        await asyncio.sleep(BATCH_DELAY)

    await safe_edit(st, mf(f"Added: {added}/{total} - Promoting"))

    if is_sg:
        for i in range(0, len(entities), BATCH_SIZE):
            batch = entities[i:i + BATCH_SIZE]
            promote_tasks = []
            for u, ent in batch:
                promote_tasks.append(event.client(EditAdminRequest(
                    group, ent,
                    ChatAdminRights(
                        change_info=True, post_messages=True, edit_messages=True,
                        delete_messages=True, ban_users=True, invite_users=True,
                        pin_messages=True, add_admins=True, manage_call=True,
                    ), "Bot"
                )))
            admin_results = await asyncio.gather(*promote_tasks, return_exceptions=True)
            for r in admin_results:
                if not isinstance(r, Exception):
                    admin_ok += 1
            await asyncio.sleep(BATCH_DELAY)

    await safe_edit(st, ast_ok(
        f"Bots Added · {added}/{total} | Admin · {admin_ok} | Failed · {failed}"
    ))
    await auto_del(st, 15)


# ═══════════════ 𝐊𝐄𝐄𝐏𝐀𝐋𝐈𝐕𝐄 ═══════════════
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
    print(short_ok(f"Keepalive Server · port {port}"))


# ═══════════════ 𝐑𝐄𝐏𝐋𝐘 𝐌𝐄𝐒𝐒𝐀𝐆𝐄𝐒 ═══════════════
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
    "𝐁𝐊𝐂 🦴🐕",
]

# ═══════════════ 𝐁𝐎𝐓 𝐂𝐎𝐌𝐌𝐀𝐍𝐃𝐒 ═══════════════
async def b_start(update, context):
    uid = update.effective_user.id
    name = update.effective_user.first_name or "User"
    status = "👑 " + mf("SUDO") if is_admin(uid) else "👤 " + mf("USER")
    text = (
        "╭────────────── 𓂃𓈒𓏸 ──────────────╮\n\n"
        "              " + SYLAS_DISPLAY + "\n\n"
        "        " + mf("beyond the ordinary") + "\n\n"
        "     ─────────────────────────\n\n"
       f"        " + mf("Welcome back") + ",\n"
       f"        " + mf(name) + "  ·  " + status + "\n\n"
        "     ─────────────────────────\n\n"
        "        " + mf("System") + " · " + mf("ONLINE") + "\n\n"
        "     ─────────────────────────\n\n"
        "        " + SYLAS_DISPLAY + "\n"
        "        " + MADE_BY + "\n\n"
        "╰────────────── 𓂃𓈒𓏸 ──────────────╯"
    )
    keyboard = [
        [
            InlineKeyboardButton("◈ " + mf("Commands"), callback_data="sylas_cmds"),
            InlineKeyboardButton("◈ " + mf("Status"), callback_data="sylas_status"),
        ],
        [
            InlineKeyboardButton("◈ " + mf("Owner"), callback_data="sylas_owner"),
            InlineKeyboardButton("◈ " + mf("About"), callback_data="sylas_about"),
        ],
    ]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


async def b_menu(update, context):
    if not acquire_reply_lock("menu", update.effective_chat.id):
        return
    bot = await context.bot.get_me()
    uid = update.effective_user.id
    status = "👑 " + mf("SUDO") if is_admin(uid) else "👤 " + mf("USER")
    await update.message.reply_text(build_menu(bot.username, status))


async def b_ping(update, context):
    if not acquire_reply_lock("ping", update.effective_chat.id):
        return
    t0 = time.perf_counter()
    m = await update.message.reply_text("𝑺ʏ𝐋ꪖs ʙᴏᴛ\n\n⚡ ...")
    t1 = time.perf_counter()
    ms = int((t1 - t0) * 1000)
    try:
        await m.edit_text(f"𝑺ʏ𝐋ꪖs ʙᴏᴛ\n\n⚡ {ms}ms")
    except Exception:
        pass
    await auto_del(m)


async def b_tts(update, context):
    if not context.args:
        await update.message.reply_text(ast_info("Usage · /tts <text>"))
        return
    text = " ".join(context.args)
    chat_id = update.effective_chat.id
    msg = await update.message.reply_text(short_info("Generating TTS"))
    try:
        loop = asyncio.get_running_loop()
        def gen_tts():
            path = os.path.join(tempfile.gettempdir(), f"tts_{chat_id}_{random.randint(1000, 9999)}.mp3")
            tts = gTTS(text=text, lang='hi')
            tts.save(path)
            return path
        path = await loop.run_in_executor(None, gen_tts)
        if not os.path.exists(path):
            raise Exception("File not created")
        await msg.delete()
        with open(path, 'rb') as f:
            await context.bot.send_voice(chat_id=chat_id, voice=f, caption=f"🗣️ {text[:100]}")
        try:
            os.remove(path)
        except Exception:
            pass
    except Exception as e:
        print(f"[TTS] Error: {e}")
        try:
            await msg.edit_text(ast_err("TTS Failed · shorter text"))
        except Exception:
            await context.bot.send_message(chat_id=chat_id, text=ast_err("TTS Failed"))


async def b_ttsja(update, context):
    if not context.args:
        await update.message.reply_text(ast_info("Usage · /ttsja <text>"))
        return
    text = " ".join(context.args)
    chat_id = update.effective_chat.id
    msg = await update.message.reply_text(short_info("Generating Anime Voice"))
    try:
        path = os.path.join(tempfile.gettempdir(), f"ttsja_{chat_id}_{random.randint(1000, 9999)}.mp3")
        communicate = edge_tts.Communicate(text, "ja-JP-NanamiNeural")
        await communicate.save(path)
        await msg.delete()
        with open(path, 'rb') as f:
            await context.bot.send_voice(chat_id=chat_id, voice=f, caption=f"🎌 {text[:100]}")
        try:
            os.remove(path)
        except Exception:
            pass
    except Exception:
        try:
            path = os.path.join(tempfile.gettempdir(), f"ttsja_{chat_id}_{random.randint(1000, 9999)}.mp3")
            tts = gTTS(text=text, lang='ja')
            tts.save(path)
            await msg.delete()
            with open(path, 'rb') as f:
                await context.bot.send_voice(chat_id=chat_id, voice=f, caption=f"🎌 {text[:100]}")
            try:
                os.remove(path)
            except Exception:
                pass
        except Exception:
            try:
                await msg.edit_text(ast_err("Anime TTS Failed"))
            except Exception:
                pass


# ═══════════════ 𝐌𝐔𝐓𝐄 / 𝐔𝐍𝐌𝐔𝐓𝐄 ═══════════════
async def b_mute(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not acquire_reply_lock("mute", update.effective_chat.id):
        return
    chat_id = update.effective_chat.id
    target_id = None
    if update.message.reply_to_message:
        target_id = update.message.reply_to_message.from_user.id
    elif context.args:
        try:
            target_id = int(context.args[0])
        except Exception:
            pass
    if not target_id:
        await update.message.reply_text(ast_info("Reply or ID · /mute"))
        return
    try:
        await context.bot.restrict_chat_member(
            chat_id, target_id,
            permissions=ChatPermissions(can_send_messages=False)
        )
        await update.message.reply_text(ast_ok("Muted"))
    except Exception as e:
        await update.message.reply_text(ast_err(f"Failed · {str(e)[:50]}"))


async def b_unmute(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not acquire_reply_lock("unmute", update.effective_chat.id):
        return
    chat_id = update.effective_chat.id
    target_id = None
    if update.message.reply_to_message:
        target_id = update.message.reply_to_message.from_user.id
    elif context.args:
        try:
            target_id = int(context.args[0])
        except Exception:
            pass
    if not target_id:
        await update.message.reply_text(ast_info("Reply or ID · /unmute"))
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
                can_pin_messages=False,
            )
        )
        await update.message.reply_text(ast_ok("Unmuted"))
    except Exception as e:
        await update.message.reply_text(ast_err(f"Failed · {str(e)[:50]}"))
        # ═══════════════ 𝐀𝐃𝐌𝐈𝐍 ═══════════════
async def b_admin(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not acquire_reply_lock("admin", update.effective_chat.id):
        return
    chat_id = update.effective_chat.id
    if not ALL_BOT_APPS:
        await update.message.reply_text(ast_err("No Bots Active"))
        return
    msg = await update.message.reply_text(short_info("Promoting Bots · parallel"))
    promoted = 0
    already = 0
    failed = 0
    lock = asyncio.Lock()

    async def op(bot_app):
        nonlocal promoted, already, failed
        try:
            bot = await bot_app.bot.get_me()
            try:
                member = await context.bot.get_chat_member(chat_id, bot.id)
                if member.status in ['administrator', 'creator']:
                    async with lock:
                        already += 1
                    return
            except Exception:
                pass
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
            async with lock:
                promoted += 1
        except Exception:
            async with lock:
                failed += 1

    await asyncio.gather(*[op(b) for b in list(ALL_BOT_APPS)])
    await msg.edit_text(
        ast_ok(f"Promoted · {promoted} | Already · {already} | Failed · {failed}")
    )


async def b_adminoff(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not acquire_reply_lock("adminoff", update.effective_chat.id):
        return
    chat_id = update.effective_chat.id

    async def op(bot_app):
        bot = await bot_app.bot.get_me()
        await context.bot.promote_chat_member(
            chat_id, bot.id,
            can_change_info=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False,
            can_manage_video_chats=False,
            can_manage_chat=False,
        )

    r = await _parallel_bot_op("adminoff", op)
    await update.message.reply_text(ast_ok(f"{r['ok']} Bots Demoted"))


# ═══════════════ 𝐒𝐔𝐃𝐎 ═══════════════
async def b_legarib(update, context):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not acquire_reply_lock("legarib", update.effective_chat.id):
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
        except Exception:
            await update.message.reply_text(ast_info("Reply or ID · /legarib"))
            return
    else:
        await update.message.reply_text(ast_info("Reply or ID · /legarib"))
        return
    if target_id in ADMIN_IDS:
        await update.message.reply_text(ast_warn("Already Sudo"))
        return
    ADMIN_IDS.add(target_id)
    await update.message.reply_text(
        ast_ok(f"Sudo Granted · {target_name} · {target_id}")
    )


async def b_hatgarib(update, context):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not acquire_reply_lock("hatgarib", update.effective_chat.id):
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
        except Exception:
            return
    else:
        await update.message.reply_text(ast_info("Reply or ID · /hatgarib"))
        return
    if target_id == OWNER_ID:
        await update.message.reply_text(ast_err("Cannot remove Owner"))
        return
    if target_id in ADMIN_IDS:
        ADMIN_IDS.discard(target_id)
        await update.message.reply_text(
            ast_ok(f"Sudo Revoked · {target_name} · {target_id}")
        )
    else:
        await update.message.reply_text(ast_info("User not Sudo"))


async def b_garibokilist(update, context):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not acquire_reply_lock("garibokilist", update.effective_chat.id):
        return
    lines = [mf("GARIBOKI LIST") + "\n"]
    for i, uid in enumerate(sorted(ADMIN_IDS), 1):
        crown = "👑" if uid == OWNER_ID else "🔹"
        try:
            user = await context.bot.get_chat(uid)
            name = user.first_name
            username = f"@{user.username}" if user.username else ""
            lines.append(f"{crown} {i}. {name} {username} (`{uid}`)")
        except Exception:
            lines.append(f"{crown} {i}. Unknown (`{uid}`)")
    lines.append(f"\nTotal Sudo: {len(ADMIN_IDS)}")
    await update.message.reply_text("\n".join(lines))


# ═══════════════ 𝐇𝐎𝐒𝐓𝐈𝐍𝐆 ═══════════════
async def b_addhost(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not context.args:
        await update.message.reply_text(ast_info("Usage · /addhost <bot_token>"))
        return
    token = context.args[0].strip()
    user_id = str(update.effective_user.id)
    msg = await update.message.reply_text(short_info("Validating Token"))
    try:
        test_bot = Bot(token)
        bot_info = await test_bot.get_me()
        await test_bot.close()
        if user_id not in HOSTED_BOTS:
            HOSTED_BOTS[user_id] = []
        for bot in HOSTED_BOTS[user_id]:
            if bot['token'] == token:
                await msg.edit_text(ast_warn("Bot Already Hosted"))
                return
        if len(HOSTED_BOTS[user_id]) >= 5:
            await msg.edit_text(ast_err("Max 5 Bots Per Sudo"))
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
        asyncio.create_task(
            run_bot(token, HOSTED_BOT_COUNTER, get_proxy(HOSTED_BOT_COUNTER), hosted=True)
        )
        await msg.edit_text(ast_ok(f"Bot Hosted · @{bot_info.username} · #{HOSTED_BOT_COUNTER}"))
    except Exception as e:
        await msg.edit_text(ast_err(f"Invalid Token · {str(e)[:50]}"))


async def b_mybots(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNSUDO_MSG)
        return
    user_id = str(update.effective_user.id)
    if user_id not in HOSTED_BOTS or not HOSTED_BOTS[user_id]:
        await update.message.reply_text(ast_info("No hosted bots · /addhost <token>"))
        return
    lines = [mf("YOUR HOSTED BOTS") + "\n"]
    for i, bot in enumerate(HOSTED_BOTS[user_id], 1):
        lines.append(f"{i}. @{bot['username']} - {bot['name']}")
    lines.append(f"\nTotal: {len(HOSTED_BOTS[user_id])}")
    await update.message.reply_text("\n".join(lines))


async def b_removehost(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not context.args:
        await update.message.reply_text(ast_info("Usage · /removehost <username>"))
        return
    username = context.args[0].replace("@", "").strip()
    user_id = str(update.effective_user.id)
    if user_id not in HOSTED_BOTS:
        await update.message.reply_text(ast_err("No Bots"))
        return
    for bot in HOSTED_BOTS[user_id]:
        if bot['username'] == username:
            HOSTED_BOTS[user_id].remove(bot)
            save_hosted_bots()
            await update.message.reply_text(ast_ok(f"Removed · @{username}"))
            return
    await update.message.reply_text(ast_err(f"Not Found · @{username}"))


async def b_hostlist(update, context):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not HOSTED_BOTS:
        await update.message.reply_text(ast_info("No Hosted Bots"))
        return
    total = 0
    lines = [mf("ALL HOSTED BOTS") + "\n"]
    for user_id, bots in HOSTED_BOTS.items():
        try:
            user = await context.bot.get_chat(int(user_id))
            name = user.first_name
        except Exception:
            name = user_id
        lines.append(f"👤 {name}:")
        for bot in bots:
            lines.append(f"  └ @{bot['username']} - {bot['name']}")
            total += 1
    lines.append(f"\nTotal Bots: {total}\nUsers: {len(HOSTED_BOTS)}")
    await update.message.reply_text("\n".join(lines))


# ═══════════════ 𝐑𝐄𝐏𝐋𝐘 / 𝐑𝐑 𝐖𝐎𝐑𝐊𝐄𝐑𝐒 ═══════════════
async def reply_worker(bot_app, chat_id, name, task_id, is_rr=False):
    pending_dict = PENDING_RR if is_rr else PENDING_REPLIES
    msg_list = RR_MSG if is_rr else REPLY_MSG
    tasks_dict = RR_TASKS if is_rr else REPLY_TASKS
    sem = get_sem(id(bot_app))
    while tasks_dict.get(task_id, {}).get('running', False):
        try:
            if chat_id in pending_dict and pending_dict[chat_id]:
                msg_id = pending_dict[chat_id].pop(0)
                text = random.choice(msg_list).format(target=name)
                async with sem:
                    await bot_app.bot.send_message(
                        chat_id=chat_id,
                        text=text,
                        reply_to_message_id=msg_id
                    )
                GLOBAL_STATS["replies_sent"] += 1
                await asyncio.sleep(0.02)
            else:
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(int(e.retry_after) + RETRY_AFTER_BUFFER)
        except Exception:
            await asyncio.sleep(0.1)


async def b_reply(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not acquire_reply_lock("reply", update.effective_chat.id):
        return
    if not context.args:
        await update.message.reply_text(ast_info("Usage · /reply <name>"))
        return
    name = " ".join(context.args)
    chat_id = update.effective_chat.id
    if chat_id in REPLY_TASKS and REPLY_TASKS[chat_id]['running']:
        REPLY_TASKS[chat_id]['running'] = False
        await asyncio.sleep(0.2)
        for w in REPLY_TASKS[chat_id].get('workers', []):
            w.cancel()
    REPLY_TASKS[chat_id] = {'name': name, 'running': True, 'workers': []}
    PENDING_REPLIES[chat_id] = []
    for bot_app in list(ALL_BOT_APPS):
        task = asyncio.create_task(reply_worker(bot_app, chat_id, name, chat_id))
        REPLY_TASKS[chat_id]['workers'].append(task)
    await update.message.reply_text(ast_ok(f"Reply Started · {name}"))


async def b_stopreply(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not acquire_reply_lock("stopreply", update.effective_chat.id):
        return
    chat_id = update.effective_chat.id
    if chat_id in REPLY_TASKS and REPLY_TASKS[chat_id]['running']:
        REPLY_TASKS[chat_id]['running'] = False
        await asyncio.sleep(0.2)
        for w in REPLY_TASKS[chat_id].get('workers', []):
            w.cancel()
        del REPLY_TASKS[chat_id]
        if chat_id in PENDING_REPLIES:
            del PENDING_REPLIES[chat_id]
        await update.message.reply_text(ast_ok("Reply Stopped"))
    else:
        await update.message.reply_text(ast_info("Nothing Active · Reply"))


async def b_rr(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not acquire_reply_lock("rr", update.effective_chat.id):
        return
    if not update.message.reply_to_message:
        await update.message.reply_text(ast_info("Reply to a message · /rr"))
        return
    target = update.message.reply_to_message.from_user
    if not target:
        return
    chat_id = update.effective_chat.id
    if chat_id in RR_TASKS and RR_TASKS[chat_id]['running']:
        RR_TASKS[chat_id]['running'] = False
        await asyncio.sleep(0.2)
        for w in RR_TASKS[chat_id].get('workers', []):
            w.cancel()
    RR_TASKS[chat_id] = {'name': target.first_name, 'running': True, 'workers': []}
    RR_TARGETS[chat_id] = target.id
    PENDING_RR[chat_id] = []
    for bot_app in list(ALL_BOT_APPS):
        task = asyncio.create_task(
            reply_worker(bot_app, chat_id, target.first_name, chat_id, is_rr=True)
        )
        RR_TASKS[chat_id]['workers'].append(task)
    await update.message.reply_text(ast_ok(f"RR Started · {target.first_name}"))


async def b_stoprr(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not acquire_reply_lock("stoprr", update.effective_chat.id):
        return
    chat_id = update.effective_chat.id
    if chat_id in RR_TASKS and RR_TASKS[chat_id]['running']:
        RR_TASKS[chat_id]['running'] = False
        await asyncio.sleep(0.2)
        for w in RR_TASKS[chat_id].get('workers', []):
            w.cancel()
        del RR_TASKS[chat_id]
        if chat_id in RR_TARGETS:
            del RR_TARGETS[chat_id]
        if chat_id in PENDING_RR:
            del PENDING_RR[chat_id]
        await update.message.reply_text(ast_ok("RR Stopped"))
    else:
        await update.message.reply_text(ast_info("Nothing Active · RR"))


# ═══════════════ 𝐓𝐎𝐎𝐋𝐒 ═══════════════
async def b_delay(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not acquire_reply_lock("delay", update.effective_chat.id):
        return
    if not context.args:
        await update.message.reply_text(
            ast_info(f"Current · {CHAT_DELAYS.get(update.effective_chat.id, 0)}s")
        )
        return
    try:
        d = max(0, float(context.args[0]))
    except Exception:
        await update.message.reply_text(ast_err("Invalid · /delay <sec>"))
        return
    CHAT_DELAYS[update.effective_chat.id] = d
    await update.message.reply_text(ast_ok(f"Delay · {d}s"))


async def b_purge(update, context):
    if not is_admin(update.effective_user.id):
        return
    if not update.message.reply_to_message:
        return
    if not acquire_reply_lock("purge", update.effective_chat.id):
        return
    parts = update.message.text.split()
    try:
        n = min(int(parts[1]) if len(parts) > 1 else 100, 1000)
    except Exception:
        n = 100
    rid = update.message.reply_to_message.message_id
    try:
        await update.message.delete()
    except Exception:
        pass
    d = 0
    for mid in range(rid, rid + n):
        try:
            await context.bot.delete_message(update.effective_chat.id, mid)
            d += 1
        except Exception:
            continue
        await asyncio.sleep(0.02)
    m = await context.bot.send_message(
        update.effective_chat.id,
        ast_ok(f"Purged · {d} messages")
    )
    await auto_del(m)


async def b_purgeall(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not acquire_reply_lock("purgeall", update.effective_chat.id):
        return
    parts = update.message.text.split()
    try:
        n = min(int(parts[1]) if len(parts) > 1 else 100, 1000)
    except Exception:
        n = 100
    try:
        await update.message.delete()
    except Exception:
        pass
    d = 0
    async for msg in context.bot.get_chat_history(update.effective_chat.id, limit=n):
        try:
            await msg.delete()
            d += 1
        except Exception:
            continue
        await asyncio.sleep(0.02)
    m = await context.bot.send_message(
        update.effective_chat.id,
        ast_ok(f"Purged · {d} messages")
    )
    await auto_del(m)


async def b_lock(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not acquire_reply_lock("lock", update.effective_chat.id):
        return
    no = ChatPermissions(
        can_send_messages=False,
        can_send_polls=False,
        can_send_other_messages=False,
        can_add_web_page_previews=False,
        can_change_info=False,
        can_invite_users=False,
        can_pin_messages=False,
    )
    chat_id = update.effective_chat.id

    async def op(bot_app):
        await bot_app.bot.set_chat_permissions(chat_id, no)

    r = await _parallel_bot_op("lock", op)
    if r['ok'] > 0:
        await update.message.reply_text(ast_ok(f"Locked · {r['ok']} bots"))
    else:
        await update.message.reply_text(ast_err("Failed · no bot responded"))


async def b_unlock(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not acquire_reply_lock("unlock", update.effective_chat.id):
        return
    allp = ChatPermissions(
        can_send_messages=True,
        can_send_polls=True,
        can_send_other_messages=True,
        can_add_web_page_previews=True,
        can_change_info=False,
        can_invite_users=True,
        can_pin_messages=False,
    )
    chat_id = update.effective_chat.id

    async def op(bot_app):
        await bot_app.bot.set_chat_permissions(chat_id, allp)

    r = await _parallel_bot_op("unlock", op)
    if r['ok'] > 0:
        await update.message.reply_text(ast_ok(f"Unlocked · {r['ok']} bots"))
    else:
        await update.message.reply_text(ast_err("Failed · no bot responded"))


async def b_leave(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not acquire_reply_lock("leave", update.effective_chat.id):
        return
    chat_id = update.effective_chat.id
    total = len(ALL_BOT_APPS)
    if total == 0:
        await update.message.reply_text(ast_err("No Bots Active"))
        return
    msg = await update.message.reply_text(short_info(f"Leaving · {total} bots"))
    left = 0
    not_in = 0
    failed = 0
    lock = asyncio.Lock()

    async def op(bot_app):
        nonlocal left, not_in, failed
        sem = get_sem(id(bot_app))
        async with sem:
            try:
                await bot_app.bot.leave_chat(chat_id)
                async with lock:
                    left += 1
            except Exception as e:
                err = str(e).lower()
                async with lock:
                    if (
                        "not a member" in err
                        or "user_not_participant" in err
                        or "participant" in err
                        or "chat not found" in err
                    ):
                        not_in += 1
                    else:
                        failed += 1

    await asyncio.gather(*[op(b) for b in list(ALL_BOT_APPS)])
    text = ast_ok(f"Left · {left}/{total} | Not In · {not_in} | Failed · {failed}")
    try:
        await msg.edit_text(text)
    except Exception:
        try:
            await context.bot.send_message(chat_id, text)
        except Exception:
            pass


async def b_leaveall(update, context):
    await b_leave(update, context)


async def b_stopall(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not acquire_reply_lock("stopall", update.effective_chat.id):
        return
    chat_id = update.effective_chat.id
    stopped = []
    task_dicts = [
        ("Reply", REPLY_TASKS),
        ("RR", RR_TASKS),
        ("NC", NC_TASKS),
        ("NC1", NC1_TASKS),
        ("SylasNC", SYLASNC_TASKS),
        ("Sync", SYNC_TASKS),
        ("BotNC", BOTNC_TASKS),
        ("GNC", GNC_TASKS),
        ("LNC", LNC_TASKS),
        ("SylasNC2", MNC_TASKS),
        ("RNC", RNC_TASKS),
        ("Spam", SPAM_TASKS),
        ("Spam1", SPAM1_TASKS),
        ("DSpam", DSPAM_TASKS),
        ("PicSpam", PICSPAM_TASKS),
        ("PFP", PFP_TASKS),
    ]
    for name, tasks in task_dicts:
        if chat_id in tasks and tasks[chat_id].get('running', False):
            tasks[chat_id]['running'] = False
            await asyncio.sleep(0.2)
            for w in tasks[chat_id].get('workers', []):
                w.cancel()
            del tasks[chat_id]
            stopped.append(name)
    for d in [PENDING_REPLIES, PENDING_RR]:
        if chat_id in d:
            del d[chat_id]
    if chat_id in RR_TARGETS:
        del RR_TARGETS[chat_id]
    if stopped:
        await update.message.reply_text(ast_ok(f"Stopped · {', '.join(stopped)}"))
    else:
        await update.message.reply_text(ast_info("Nothing Active"))


async def b_status(update, context):
    if not acquire_reply_lock("status", update.effective_chat.id):
        return
    uptime_secs = int(time.time() - GLOBAL_STATS["start_time"])
    h, rem = divmod(uptime_secs, 3600)
    m, s = divmod(rem, 60)
    d, h = divmod(h, 24)
    parts = []
    if d:
        parts.append(f"{d}d")
    if h:
        parts.append(f"{h}h")
    if m:
        parts.append(f"{m}m")
    parts.append(f"{s}s")
    await update.message.reply_text(
        "╭────────────── 𓂃𓈒𓏸 ──────────────╮\n\n"
        "        📊 " + mf("STATUS") + "\n\n"
        "     ─────────────────────────\n\n"
       f"        ⏱️  " + mf("Uptime") + f" · {' '.join(parts)}\n"
       f"        🤖  " + mf("Bots") + f" · {len(ALL_BOT_APPS)}\n"
       f"        💬  " + mf("Messages") + f" · {GLOBAL_STATS['messages_sent']}\n"
       f"        ↩️  " + mf("Replies") + f" · {GLOBAL_STATS['replies_sent']}\n\n"
        "╰────────────── 𓂃𓈒𓏸 ──────────────╯"
    )


async def b_uptime(update, context):
    if not acquire_reply_lock("uptime", update.effective_chat.id):
        return
    uptime_secs = int(time.time() - GLOBAL_STATS["start_time"])
    h, rem = divmod(uptime_secs, 3600)
    m, s = divmod(rem, 60)
    d, h = divmod(h, 24)
    parts = []
    if d:
        parts.append(f"{d}d")
    if h:
        parts.append(f"{h}h")
    if m:
        parts.append(f"{m}m")
    parts.append(f"{s}s")
    await update.message.reply_text(
        ast_ok(f"Uptime · {' '.join(parts)} · {len(ALL_BOT_APPS)} bots")
    )


async def b_stats(update, context):
    if not acquire_reply_lock("stats", update.effective_chat.id):
        return
    uptime_secs = int(time.time() - GLOBAL_STATS["start_time"])
    h, rem = divmod(uptime_secs, 3600)
    m, s = divmod(rem, 60)
    d, h = divmod(h, 24)
    parts = []
    if d:
        parts.append(f"{d}d")
    if h:
        parts.append(f"{h}h")
    if m:
        parts.append(f"{m}m")
    parts.append(f"{s}s")

    active_tasks = 0
    task_dicts = [
        REPLY_TASKS, RR_TASKS, NC_TASKS, NC1_TASKS, SYLASNC_TASKS,
        SYNC_TASKS, BOTNC_TASKS, GNC_TASKS, LNC_TASKS, MNC_TASKS,
        RNC_TASKS, SPAM_TASKS, SPAM1_TASKS, DSPAM_TASKS,
        PICSPAM_TASKS, PFP_TASKS,
    ]
    for d_ in task_dicts:
        for cid, data in d_.items():
            if isinstance(data, dict) and data.get('running'):
                active_tasks += 1

    await update.message.reply_text(
        "╭────────────── 𓂃𓈒𓏸 ──────────────╮\n\n"
        "        📊 " + mf("STATS") + "\n\n"
        "     ─────────────────────────\n\n"
       f"        ⏱️  " + mf("Uptime") + f" · {' '.join(parts)}\n"
       f"        🤖  " + mf("Bots") + f" · {len(ALL_BOT_APPS)}\n"
       f"        💬  " + mf("Sent") + f" · {GLOBAL_STATS['messages_sent']}\n"
       f"        ↩️  " + mf("Replies") + f" · {GLOBAL_STATS['replies_sent']}\n"
       f"        🔄  " + mf("Active Tasks") + f" · {active_tasks}\n"
       f"        👥  " + mf("Sudo") + f" · {len(ADMIN_IDS)}\n\n"
        "╰────────────── 𓂃𓈒𓏸 ──────────────╯"
    )


async def b_react(update, context):
    if not acquire_reply_lock("react", update.effective_chat.id):
        return
    chat_id = update.effective_chat.id
    if chat_id in REACT_CHATS:
        del REACT_CHATS[chat_id]
        REACT_MODE.pop(chat_id, None)
        await update.message.reply_text(ast_ok("React OFF"))
    else:
        REACT_CHATS[chat_id] = True
        REACT_MODE[chat_id] = "all"
        await update.message.reply_text(ast_ok("React ON · random emoji every msg"))


async def b_ereact(update, context):
    if not acquire_reply_lock("ereact", update.effective_chat.id):
        return
    if not context.args:
        await update.message.reply_text(ast_info("Usage · /ereact <emoji>"))
        return
    chat_id = update.effective_chat.id
    emoji = context.args[0]
    REACT_CHATS[chat_id] = True
    REACT_MODE[chat_id] = "single"
    REACT_EMOJI[chat_id] = emoji
    await update.message.reply_text(ast_ok(f"React ON · {emoji}"))


async def b_optimize(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not acquire_reply_lock("optimize", update.effective_chat.id):
        return

    msg = await update.message.reply_text(short_info("Optimizing · cleanup in progress"))

    BOT_SEMAPHORES.clear()
    CMD_REPLY_LOCK.clear()
    PENDING_REPLIES.clear()
    PENDING_RR.clear()

    orphans = 0
    task_dicts = [
        REPLY_TASKS, RR_TASKS,
        NC_TASKS, NC1_TASKS, SYLASNC_TASKS, SYNC_TASKS, BOTNC_TASKS,
        GNC_TASKS, LNC_TASKS, MNC_TASKS, RNC_TASKS,
        SPAM_TASKS, SPAM1_TASKS, DSPAM_TASKS,
        PICSPAM_TASKS, PFP_TASKS,
    ]
    for d in task_dicts:
        for chat_id in list(d.keys()):
            if not d[chat_id].get('running', False):
                for w in d[chat_id].get('workers', []):
                    if not w.done():
                        w.cancel()
                del d[chat_id]
                orphans += 1

    GLOBAL_STATS["start_time"] = time.time()

    status = (
        f"✅ Optimize Complete\n"
        f"├ Semaphores: reset\n"
        f"├ Reply locks: cleared\n"
        f"├ Orphan tasks: {orphans} cleaned\n"
        f"├ Active bots: {len(ALL_BOT_APPS)}\n"
        f"└ Uptime: reset"
    )
    await msg.edit_text(ast_ok(status))


# ═══════════════ 𝐍𝐂 𝐖𝐎𝐑𝐃𝐒 ═══════════════
NC_WORDS = [
    "𝘾𝙃𝙐𝘿𝘼𝙄 𝘼𝙍𝘾〘🤍〙 જ⁀➴🤍જ⁀➴🤍જ⁀➴🤍જ⁀➴🤍",
    "𝘾𝙃𝙐𝘿𝘼𝙄 𝘼𝙍𝘾〘❤️〙 જ⁀➴❤️જ⁀➴❤️જ⁀➴❤️જ⁀➴❤️",
    "𝘾𝙃𝙐𝘿𝘼𝙄 𝘼𝙍𝘾〘🧡〙 જ⁀➴🧡જ⁀➴🧡જ⁀➴🧡જ⁀➴🧡",
    "𝘾𝙃𝙐𝘿𝘼𝙄 𝘼𝙍𝘾〘💛〙 જ⁀➴💛જ⁀➴💛જ⁀➴💛જ⁀➴💛",
    "𝘾𝙃𝙐𝘿𝘼𝙄 𝘼𝙍𝘾〘💚〙 જ⁀➴💚જ⁀➴💚જ⁀➴💚જ⁀➴💚",
    "𝘾𝙃𝙐𝘿𝘼𝙄 𝘼𝙍𝘾〘🩵〙 જ⁀➴🩵જ⁀➴🩵જ⁀➴🩵જ⁀➴🩵",
    "𝘾𝙃𝙐𝘿𝘼𝙄 𝘼𝙍𝘾〘💙〙 જ⁀➴💙જ⁀➴💙જ⁀➴💙જ⁀➴💙",
    "𝘾𝙃𝙐𝘿𝘼𝙄 𝘼𝙍𝘾〘💜〙 જ⁀➴💜જ⁀➴💜જ⁀➴💜જ⁀➴💜",
    "𝘾𝙃𝙐𝘿𝘼𝙄 𝘼𝙍𝘾〘🤎〙 જ⁀➴🤎જ⁀➴🤎જ⁀➴🤎જ⁀➴🤎",
    "𝘾𝙃𝙐𝘿𝘼𝙄 𝘼𝙍𝘾〘🖤〙 જ⁀➴🖤જ⁀➴🖤જ⁀➴🖤જ⁀➴🖤",
    "𝘾𝙃𝙐𝘿𝘼𝙄 𝘼𝙍𝘾〘🩶〙 જ⁀➴🩶જ⁀➴🩶જ⁀➴🩶જ⁀➴🩶",
    "𝘾𝙃𝙐𝘿𝘼𝙄 𝘼𝙍𝘾〘🩷〙 જ⁀➴🩷જ⁀➴🩷જ⁀➴🩷જ⁀➴🩷",
]
NC_PATTERN = "{text} {word} . ݁₊ ⊹ . ݁  <{emoji}> . ݁₊ ⊹ . ݁"
NC_EMOJIS = ["🔥", "💀", "⚡", "🖤", "❤️", "🤍", "💫", "🌪️", "👑", "💥", "🎀", "🩵"]
NC_TASKS = {}
NC_TARGETS = {}

NC1_EMOJIS = [
    "🤍", "🖤", "💛", "❤️", "🩷", "💜", "💙", "🩵", "💚", "🧡", "🤎", "🩶",
    "💎", "👑", "🔥", "💀", "⚡", "🌟", "✨", "💫", "🪐", "🎀", "💥", "🌪️"
]
NC1_TASKS = {}
NC1_TARGETS = {}

SYLASNC_EMOJIS = ["🦴", "🤣", "💋", "💀", "🔥", "⚡", "👑", "🖤", "🤍", "❤️", "🩷", "💜"]
SYLASNC_TASKS = {}
SYLASNC_TARGETS = {}

SYNC_SYMBOLS = ["𒈙"]
SYNC_EMOJIS = ["☢️", "🩷", "🔥", "🦈", "👾", "❄️", "💠", "🀄", "🧃", "☀️", "🫧", "🥁", "💀", "🖤", "🌟"]
SYNC_END = ["ᑕʜꪊD"]
SYNC_TASKS = {}
SYNC_TARGETS = {}

BOTNC_WORDS = [
    "{target} 🤍 White Bot Se ᴛᴇʀɪ ᴍᴀᴀ ᴄʜᴜᴅᴇɢɪ ᴊᴀʙ ᴛᴀᴋ ɴᴀʜɪ ᴛᴏʀᴛᴜɢᴀ",
    "{target} 🖤 Black Bot Se ᴛᴇʀɪ ᴍᴀᴀ ᴄʜᴜᴅᴇɢɪ ᴊᴀʙ ᴛᴀᴋ ɴᴀʜɪ ᴛᴏʀᴛᴜɢᴀ",
    "{target} 💛 Yellow Bot Se ᴛᴇʀɪ ᴍᴀᴀ ᴄʜᴜᴅᴇɢɪ ᴊᴀʙ ᴛᴀᴋ ɴᴀʜɪ ᴛᴏʀᴛᴜɢᴀ",
    "{target} ❤️ Red Bot Se ᴛᴇʀɪ ᴍᴀᴀ ᴄʜᴜᴅᴇɢɪ ᴊᴀʙ ᴛᴀᴋ ɴᴀʜɪ ᴛᴏʀᴛᴜɢᴀ",
    "{target} 🩷 Pink Bot Se ᴛᴇʀɪ ᴍᴀᴀ ᴄʜᴜᴅᴇɢɪ ᴊᴀʙ ᴛᴀᴋ ɴᴀʜɪ ᴛᴏʀᴛᴜɢᴀ",
    "{target} 💜 Purple Bot Se ᴛᴇʀɪ ᴍᴀᴀ ᴄʜᴜᴅᴇɢɪ ᴊᴀʙ ᴛᴀᴋ ɴᴀʜɪ ᴛᴏʀᴛᴜɢᴀ",
    "{target} 💙 Blue Bot Se ᴛᴇʀɪ ᴍᴀᴀ ᴄʜᴜᴅᴇɢɪ ᴊᴀʙ ᴛᴀᴋ ɴᴀʜɪ ᴛᴏʀᴛᴜɢᴀ",
    "{target} 🩵 Sky Blue Bot Se ᴛᴇʀɪ ᴍᴀᴀ ᴄʜᴜᴅᴇɢɪ ᴊᴀʙ ᴛᴀᴋ ɴᴀʜɪ ᴛᴏʀᴛᴜɢᴀ",
    "{target} 💚 Green Bot Se ᴛᴇʀɪ ᴍᴀᴀ ᴄʜᴜᴅᴇɢɪ ᴊᴀʙ ᴛᴀᴋ ɴᴀʜɪ ᴛᴏʀᴛᴜɢᴀ",
    "{target} 🧡 Orange Bot Se ᴛᴇʀɪ ᴍᴀᴀ ᴄʜᴜᴅᴇɢɪ ᴊᴀʙ ᴛᴀᴋ ɴᴀʜɪ ᴛᴏʀᴛᴜɢᴀ",
    "{target} 🤎 Brown Bot Se ᴛᴇʀɪ ᴍᴀᴀ ᴄʜᴜᴅᴇɢɪ ᴊᴀʙ ᴛᴀᴋ ɴᴀʜɪ ᴛᴏʀᴛᴜɢᴀ",
    "{target} 🩶 Grey Bot Se ᴛᴇʀɪ ᴍᴀᴀ ᴄʜᴜᴅᴇɢɪ ᴊᴀʙ ᴛᴀᴋ ɴᴀʜɪ ᴛᴏʀᴛᴜɢᴀ",
    "{target} 💎 Silver Bot Se ᴛᴇʀɪ ᴍᴀᴀ ᴄʜᴜᴅᴇɢɪ ᴊᴀʙ ᴛᴀᴋ ɴᴀʜɪ ᴛᴏʀᴛᴜɢᴀ",
    "{target} 👑 Gold Bot Se ᴛᴇʀɪ ᴍᴀᴀ ᴄʜᴜᴅᴇɢɪ ᴊᴀʙ ᴛᴀᴋ ɴᴀʜɪ ᴛᴏʀᴛᴜɢᴀ",
]
BOTNC_TASKS = {}
BOTNC_TARGETS = {}

GNC_WORDS = [
    'Hi tmkc 🐐',
    'Hi tmkl 🐐',
    'Hi bkl 🐐',
    'Hi rndike 🐐',
    'Hi tmkc bhosdike 🐐',
    'Hi gandu 🐐',
    'Hi chutiye 🐐',
    'Hi harami 🐐',
    'Hi madarchod 🐐',
    'Hi bhosdike 🐐',
]
GNC_TASKS = {}
GNC_TARGETS = {}

LNC_TASKS = {}
LNC_TARGETS = {}
LNC_EMOJIS = ["🍭", "🍬", "🧁", "🍫", "🍩", "🍪", "🎂", "🍰", "🍮", "🧸", "🎀", "🩷"]

MNC_TASKS = {}
MNC_TARGETS = {}

RNC_TASKS = {}
RNC_TARGETS = {}


def gen_nc(target=""):
    word = random.choice(NC_WORDS)
    emoji = random.choice(NC_EMOJIS)
    prefix = f"{target} " if target else ""
    return (prefix + NC_PATTERN.format(text="", word=word, emoji=emoji).strip())[:128]


def gen_nc1(target):
    e = random.choice(NC1_EMOJIS)
    return f"{target} ᴛᴇʀɪ ᴍᴀᴀ ʀᴀɴᴅɪ ʙᴀɴᴇɢɪ ) {e} ("[:128]


def gen_sylasnc(target):
    e = random.choice(SYLASNC_EMOJIS)
    return f"{target} 𝐒ꪗ𝖫𝗔s ᗷᴀᴀᴘ ᕼᴀɪ ᖇᵉᵉ{e}"[:128]


def gen_sync(n=0, target=""):
    sym = random.choice(SYNC_SYMBOLS)
    em = random.choice(SYNC_EMOJIS)
    end = random.choice(SYNC_END)
    prefix = f"{target} " if target else ""
    return (
        f"{prefix}〔 {n} 〕{sym * 9}{em}{sym * 9}{em}{sym * 9}{em}"
        f"{sym * 9}{em}{sym * 9}{em}{sym * 9}{em}{sym * 9}{em}"
        f"{sym * 9}{em}{sym * 9}{em} {end}"
    )[:128]


def gen_gnc(target="", pinned_word=None):
    word = pinned_word if pinned_word else random.choice(GNC_WORDS)
    return word[:128]


def gen_lnc(target=""):
    e = random.choice(LNC_EMOJIS)
    prefix = f"{target} " if target else ""
    return f"{prefix}ʟᴜɴ ᴄʜᴜs {e}"[:128]


MNC_EMOJIS = ["👹", "🔥", "💀", "⚡", "🐐", "💥", "😈", "👿"]

def gen_mnc(target=""):
    t = target.upper() if target else "CHUTIYA"
    e = random.choice(MNC_EMOJIS)
    return f"{e} 𝐒ʏʟᴀs 𝐓ᴇʀɪ 𝐌ᴀ ᴄᴏᴅ ɴᴇ ᴀᴀ ɢʏᴀ ({t}) {e}"


RNC_EMOJIS = ["⭐", "🌟", "✨", "💫", "🌠", "💥"]

def gen_rnc(target=""):
    t = target.upper() if target else "CHUTIYA"
    e = random.choice(RNC_EMOJIS)
    return f"{e} 𝑹ᴀɴᴅᴀ {e} sᴇ ᴄᴜᴅ » ({t})"


# ═══════════════ 𝐍𝐂 𝐖𝐎𝐑𝐊𝐄𝐑𝐒 ═══════════════
async def nc_worker(bot_app, chat_id, task_id):
    while NC_TASKS.get(task_id, {}).get('running', False):
        try:
            target = NC_TARGETS.get(chat_id, "")
            async with get_sem(id(bot_app)):
                await bot_app.bot.set_chat_title(chat_id, gen_nc(target))
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(int(e.retry_after) + RETRY_AFTER_BUFFER)
        except Exception as e:
            err = str(e).lower()
            if "not enough rights" in err or "chat_admin_required" in err:
                await asyncio.sleep(1)
            else:
                await asyncio.sleep(0.03)


async def nc1_worker(bot_app, chat_id, task_id):
    while NC1_TASKS.get(task_id, {}).get('running', False):
        try:
            target = NC1_TARGETS.get(chat_id, "Chutiya")
            async with get_sem(id(bot_app)):
                await bot_app.bot.set_chat_title(chat_id, gen_nc1(target))
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(int(e.retry_after) + RETRY_AFTER_BUFFER)
        except Exception as e:
            err = str(e).lower()
            if "not enough rights" in err or "chat_admin_required" in err:
                await asyncio.sleep(1)
            else:
                await asyncio.sleep(0.03)


async def sylasnc_worker(bot_app, chat_id, task_id):
    while SYLASNC_TASKS.get(task_id, {}).get('running', False):
        try:
            target = SYLASNC_TARGETS.get(chat_id, "Chutiya")
            async with get_sem(id(bot_app)):
                await bot_app.bot.set_chat_title(chat_id, gen_sylasnc(target))
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(int(e.retry_after) + RETRY_AFTER_BUFFER)
        except Exception as e:
            err = str(e).lower()
            if "not enough rights" in err or "chat_admin_required" in err:
                await asyncio.sleep(1)
            else:
                await asyncio.sleep(0.03)


async def sync_worker(bot_app, chat_id, task_id):
    while SYNC_TASKS.get(task_id, {}).get('running', False):
        try:
            target = SYNC_TASKS[task_id].get('target', "")
            title = SYNC_TASKS[task_id].get('title') or gen_sync(0, target)
            async with get_sem(id(bot_app)):
                await bot_app.bot.set_chat_title(chat_id, title)
            await asyncio.sleep(0.05)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(int(e.retry_after) + RETRY_AFTER_BUFFER)
        except Exception:
            await asyncio.sleep(0.05)


async def sync_ticker(chat_id, task_id):
    while SYNC_TASKS.get(task_id, {}).get('running', False):
        await asyncio.sleep(0.3)
        if not SYNC_TASKS.get(task_id, {}).get('running'):
            break
        tick = SYNC_TASKS[task_id].get('tick', 0) + 1
        target = SYNC_TASKS[task_id].get('target', "")
        SYNC_TASKS[task_id]['tick'] = tick
        SYNC_TASKS[task_id]['title'] = gen_sync(tick, target)


async def botnc_worker(bot_app, chat_id, task_id):
    idx = 0
    while BOTNC_TASKS.get(task_id, {}).get('running', False):
        try:
            target = BOTNC_TARGETS.get(chat_id, "Chutiya")
            word = BOTNC_WORDS[idx % len(BOTNC_WORDS)].format(target=target)
            async with get_sem(id(bot_app)):
                await bot_app.bot.set_chat_title(chat_id, word[:128])
            idx += 1
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(int(e.retry_after) + RETRY_AFTER_BUFFER)
        except Exception as e:
            err = str(e).lower()
            if "not enough rights" in err or "chat_admin_required" in err:
                await asyncio.sleep(1)
            else:
                await asyncio.sleep(0.03)


async def gnc_worker(bot_app, chat_id, task_id):
    while GNC_TASKS.get(task_id, {}).get('running', False):
        try:
            target = GNC_TARGETS.get(chat_id, "")
            pinned = GNC_TASKS.get(task_id, {}).get('pinned_word')
            async with get_sem(id(bot_app)):
                await bot_app.bot.set_chat_title(chat_id, gen_gnc(target, pinned))
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(int(e.retry_after) + RETRY_AFTER_BUFFER)
        except Exception as e:
            err = str(e).lower()
            if "not enough rights" in err or "chat_admin_required" in err:
                await asyncio.sleep(1)
            else:
                await asyncio.sleep(0.03)


async def lnc_worker(bot_app, chat_id, task_id):
    while LNC_TASKS.get(task_id, {}).get('running', False):
        try:
            target = LNC_TARGETS.get(chat_id, "")
            async with get_sem(id(bot_app)):
                await bot_app.bot.set_chat_title(chat_id, gen_lnc(target))
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(int(e.retry_after) + RETRY_AFTER_BUFFER)
        except Exception as e:
            err = str(e).lower()
            if "not enough rights" in err or "chat_admin_required" in err:
                await asyncio.sleep(1)
            else:
                await asyncio.sleep(0.03)


async def mnc_worker(bot_app, chat_id, task_id):
    while MNC_TASKS.get(task_id, {}).get('running', False):
        try:
            target = MNC_TARGETS.get(chat_id, "Chutiya")
            async with get_sem(id(bot_app)):
                await bot_app.bot.set_chat_title(chat_id, gen_mnc(target))
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(int(e.retry_after) + RETRY_AFTER_BUFFER)
        except Exception as e:
            err = str(e).lower()
            if "not enough rights" in err or "chat_admin_required" in err:
                await asyncio.sleep(1)
            else:
                await asyncio.sleep(0.03)


async def rnc_worker(bot_app, chat_id, task_id):
    while RNC_TASKS.get(task_id, {}).get('running', False):
        try:
            target = RNC_TARGETS.get(chat_id, "Chutiya")
            async with get_sem(id(bot_app)):
                await bot_app.bot.set_chat_title(chat_id, gen_rnc(target))
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(int(e.retry_after) + RETRY_AFTER_BUFFER)
        except Exception as e:
            err = str(e).lower()
            if "not enough rights" in err or "chat_admin_required" in err:
                await asyncio.sleep(1)
            else:
                await asyncio.sleep(0.03)


# ═══════════════ 𝐏𝐈𝐂𝐒𝐏𝐀𝐌 𝐖𝐎𝐑𝐊𝐄𝐑 ═══════════════
async def picspam_worker(bot_app, chat_id, task_id):
    sem = get_sem(id(bot_app))
    while PICSPAM_TASKS.get(task_id, {}).get('running', False):
        try:
            media_list = PICSPAM_MEDIA.get(chat_id, [])
            if not media_list:
                await asyncio.sleep(0.5)
                continue
            file_id = random.choice(media_list)
            async with sem:
                await bot_app.bot.send_photo(chat_id=chat_id, photo=file_id)
            GLOBAL_STATS["messages_sent"] += 1
            await asyncio.sleep(0.02)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(int(e.retry_after) + RETRY_AFTER_BUFFER)
        except Exception:
            await asyncio.sleep(0.1)


# ═══════════════ 𝐏𝐅𝐏 𝐖𝐎𝐑𝐊𝐄𝐑 (Endless Loop) ═══════════════
async def pfp_worker(bot_app, chat_id, task_id):
    while PFP_TASKS.get(task_id, {}).get('running', False):
        try:
            media_list = PFP_MEDIA.get(chat_id, [])
            if not media_list:
                await asyncio.sleep(0.5)
                continue
            fid = random.choice(media_list)
            try:
                file = await bot_app.bot.get_file(fid)
                tmp = os.path.join(
                    tempfile.gettempdir(),
                    f"pfp_{chat_id}_{int(time.time()*1000)}_{random.randint(100,999)}.jpg"
                )
                await file.download_to_drive(tmp)
                with open(tmp, 'rb') as f:
                    await bot_app.bot.set_chat_photo(chat_id=chat_id, photo=f)
                try:
                    os.remove(tmp)
                except Exception:
                    pass
                print(f"[PFP] ✓ {chat_id}")
            except RetryAfter as e:
                await asyncio.sleep(int(e.retry_after) + 2)
                continue
            except Exception as e:
                print(f"[PFP] err: {str(e)[:80]}")
                await asyncio.sleep(2)
                continue
            await asyncio.sleep(5)
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"[PFP] outer: {e}")
            await asyncio.sleep(1)
            # ═══════════════ 𝐍𝐂 𝐂𝐎𝐌𝐌𝐀𝐍𝐃𝐒 ═══════════════
async def _start_nc(update, context, cmd_name, task_dict, target_dict, worker_func, label, pin_word=None):
    chat_id = update.effective_chat.id
    if not ALL_BOT_APPS:
        await update.message.reply_text(ast_err("No Bots Active"))
        return
    target = pick_target(update, context, default="")
    if chat_id in task_dict and task_dict[chat_id].get('running'):
        task_dict[chat_id]['running'] = False
        await asyncio.sleep(0.2)
        for w in task_dict[chat_id].get('workers', []):
            w.cancel()
    task_dict[chat_id] = {'running': True, 'workers': []}
    if pin_word:
        task_dict[chat_id]['pinned_word'] = pin_word
    target_dict[chat_id] = target
    workers = 0
    for bot_app in list(ALL_BOT_APPS):
        task = asyncio.create_task(worker_func(bot_app, chat_id, chat_id))
        task_dict[chat_id]['workers'].append(task)
        workers += 1
    await update.message.reply_text(
        ast_ok(f"{label} Started · {workers} bots · {target or 'no target'} · /stop{cmd_name}")
    )


async def _stop_nc(update, context, task_dict, target_dict, label):
    chat_id = update.effective_chat.id
    if chat_id in task_dict and task_dict[chat_id].get('running'):
        task_dict[chat_id]['running'] = False
        await asyncio.sleep(0.2)
        for w in task_dict[chat_id].get('workers', []):
            w.cancel()
        del task_dict[chat_id]
        if chat_id in target_dict:
            del target_dict[chat_id]
        await update.message.reply_text(ast_ok(f"{label} Stopped"))
    else:
        await update.message.reply_text(ast_info(f"Nothing Active · {label}"))


async def b_nc(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not acquire_reply_lock("nc", update.effective_chat.id):
        return
    await _start_nc(update, context, "nc", NC_TASKS, NC_TARGETS, nc_worker, "NC")


async def b_stopnc(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not acquire_reply_lock("stopnc", update.effective_chat.id):
        return
    await _stop_nc(update, context, NC_TASKS, NC_TARGETS, "NC")


async def b_nc1(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not acquire_reply_lock("nc1", update.effective_chat.id):
        return
    await _start_nc(update, context, "nc1", NC1_TASKS, NC1_TARGETS, nc1_worker, "NC1")


async def b_stopnc1(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not acquire_reply_lock("stopnc1", update.effective_chat.id):
        return
    await _stop_nc(update, context, NC1_TASKS, NC1_TARGETS, "NC1")


async def b_sylasnc(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not acquire_reply_lock("sylasnc", update.effective_chat.id):
        return
    await _start_nc(update, context, "sylasnc", SYLASNC_TASKS, SYLASNC_TARGETS, sylasnc_worker, "SylasNC")


async def b_stopsylasnc(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not acquire_reply_lock("stopsylasnc", update.effective_chat.id):
        return
    await _stop_nc(update, context, SYLASNC_TASKS, SYLASNC_TARGETS, "SylasNC")


async def b_sync(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not acquire_reply_lock("sync", update.effective_chat.id):
        return
    chat_id = update.effective_chat.id
    if not ALL_BOT_APPS:
        await update.message.reply_text(ast_err("No Bots Active"))
        return
    target = pick_target(update, context, default="")
    if chat_id in SYNC_TASKS and SYNC_TASKS[chat_id].get('running'):
        SYNC_TASKS[chat_id]['running'] = False
        await asyncio.sleep(0.2)
        for w in SYNC_TASKS[chat_id].get('workers', []):
            w.cancel()
    SYNC_TASKS[chat_id] = {
        'running': True,
        'workers': [],
        'tick': 0,
        'title': gen_sync(0, target),
        'target': target,
    }
    SYNC_TARGETS[chat_id] = target
    workers = 0
    for bot_app in list(ALL_BOT_APPS):
        task = asyncio.create_task(sync_worker(bot_app, chat_id, chat_id))
        SYNC_TASKS[chat_id]['workers'].append(task)
        workers += 1
    ticker_task = asyncio.create_task(sync_ticker(chat_id, chat_id))
    SYNC_TASKS[chat_id]['workers'].append(ticker_task)
    await update.message.reply_text(
        ast_ok(f"Sync Started · {workers} bots · {target or 'no target'} · /stopsync")
    )


async def b_stopsync(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not acquire_reply_lock("stopsync", update.effective_chat.id):
        return
    await _stop_nc(update, context, SYNC_TASKS, SYNC_TARGETS, "Sync")


async def b_botnc(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not acquire_reply_lock("botnc", update.effective_chat.id):
        return
    await _start_nc(update, context, "botnc", BOTNC_TASKS, BOTNC_TARGETS, botnc_worker, "BotNC")


async def b_stopbotnc(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not acquire_reply_lock("stopbotnc", update.effective_chat.id):
        return
    await _stop_nc(update, context, BOTNC_TASKS, BOTNC_TARGETS, "BotNC")


async def b_gnc(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not acquire_reply_lock("gnc", update.effective_chat.id):
        return
    pinned = random.choice(GNC_WORDS)
    await _start_nc(update, context, "gnc", GNC_TASKS, GNC_TARGETS, gnc_worker, "GNC", pin_word=pinned)


async def b_stopgnc(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not acquire_reply_lock("stopgnc", update.effective_chat.id):
        return
    await _stop_nc(update, context, GNC_TASKS, GNC_TARGETS, "GNC")


async def b_lnc(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not acquire_reply_lock("lnc", update.effective_chat.id):
        return
    await _start_nc(update, context, "lnc", LNC_TASKS, LNC_TARGETS, lnc_worker, "LNC")


async def b_stoplnc(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not acquire_reply_lock("stoplnc", update.effective_chat.id):
        return
    await _stop_nc(update, context, LNC_TASKS, LNC_TARGETS, "LNC")


async def b_sylasnc2(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not acquire_reply_lock("sylasnc2", update.effective_chat.id):
        return
    await _start_nc(update, context, "sylasnc2", MNC_TASKS, MNC_TARGETS, mnc_worker, "SylasNC2")


async def b_stopsylasnc2(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not acquire_reply_lock("stopsylasnc2", update.effective_chat.id):
        return
    await _stop_nc(update, context, MNC_TASKS, MNC_TARGETS, "SylasNC2")


async def b_rnc(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not acquire_reply_lock("rnc", update.effective_chat.id):
        return
    await _start_nc(update, context, "rnc", RNC_TASKS, RNC_TARGETS, rnc_worker, "RNC")


async def b_stoprnc(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not acquire_reply_lock("stoprnc", update.effective_chat.id):
        return
    await _stop_nc(update, context, RNC_TASKS, RNC_TARGETS, "RNC")


# ═══════════════ 𝐏𝐈𝐂𝐒𝐏𝐀𝐌 𝐂𝐎𝐌𝐌𝐀𝐍𝐃 ═══════════════
async def b_picspam(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not acquire_reply_lock("picspam", update.effective_chat.id):
        return
    chat_id = update.effective_chat.id
    if not ALL_BOT_APPS:
        await update.message.reply_text(ast_err("No Bots Active"))
        return
    media_list = PICSPAM_MEDIA.get(chat_id, [])
    if update.message.reply_to_message and update.message.reply_to_message.photo:
        fid = update.message.reply_to_message.photo[-1].file_id
        if fid not in media_list:
            media_list.append(fid)
        PICSPAM_MEDIA[chat_id] = media_list
    if not media_list:
        await update.message.reply_text(ast_info("Reply to a photo · /picspam"))
        return
    if chat_id in PICSPAM_TASKS and PICSPAM_TASKS[chat_id].get('running'):
        PICSPAM_TASKS[chat_id]['running'] = False
        await asyncio.sleep(0.2)
        for w in PICSPAM_TASKS[chat_id].get('workers', []):
            w.cancel()
    PICSPAM_TASKS[chat_id] = {'running': True, 'workers': []}
    workers = 0
    for bot_app in list(ALL_BOT_APPS):
        task = asyncio.create_task(picspam_worker(bot_app, chat_id, chat_id))
        PICSPAM_TASKS[chat_id]['workers'].append(task)
        workers += 1
    await update.message.reply_text(
        ast_ok(f"PicSpam · {workers} bots · {len(media_list)} photos · /stoppicspam")
    )


async def b_stoppicspam(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not acquire_reply_lock("stoppicspam", update.effective_chat.id):
        return
    chat_id = update.effective_chat.id
    if chat_id in PICSPAM_TASKS and PICSPAM_TASKS[chat_id].get('running'):
        PICSPAM_TASKS[chat_id]['running'] = False
        await asyncio.sleep(0.2)
        for w in PICSPAM_TASKS[chat_id].get('workers', []):
            w.cancel()
        del PICSPAM_TASKS[chat_id]
        if chat_id in PICSPAM_MEDIA:
            del PICSPAM_MEDIA[chat_id]
        await update.message.reply_text(ast_ok("PicSpam Stopped"))
    else:
        await update.message.reply_text(ast_info("Nothing Active · PicSpam"))


# ═══════════════ 𝐏𝐅𝐏 𝐂𝐎𝐌𝐌𝐀𝐍𝐃 (Endless Loop) ═══════════════
async def b_pfp(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not acquire_reply_lock("pfp", update.effective_chat.id):
        return
    chat_id = update.effective_chat.id
    if not ALL_BOT_APPS:
        await update.message.reply_text(ast_err("No Bots Active"))
        return
    media_list = PFP_MEDIA.get(chat_id, [])
    if update.message.reply_to_message and update.message.reply_to_message.photo:
        fid = update.message.reply_to_message.photo[-1].file_id
        if fid not in media_list:
            media_list.append(fid)
        PFP_MEDIA[chat_id] = media_list
    if not media_list:
        await update.message.reply_text(ast_info("Reply to a photo · /pfp"))
        return
    if chat_id in PFP_TASKS and PFP_TASKS[chat_id].get('running'):
        PFP_TASKS[chat_id]['running'] = False
        await asyncio.sleep(0.2)
        for w in PFP_TASKS[chat_id].get('workers', []):
            w.cancel()
    PFP_TASKS[chat_id] = {'running': True, 'workers': []}
    workers = 0
    for bot_app in list(ALL_BOT_APPS):
        task = asyncio.create_task(pfp_worker(bot_app, chat_id, chat_id))
        PFP_TASKS[chat_id]['workers'].append(task)
        workers += 1
    await update.message.reply_text(
        ast_ok(f"PFP Loop · {workers} bots · {len(media_list)} photos · /stoppfp")
    )


async def b_stoppfp(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not acquire_reply_lock("stoppfp", update.effective_chat.id):
        return
    chat_id = update.effective_chat.id
    if chat_id in PFP_TASKS and PFP_TASKS[chat_id].get('running'):
        PFP_TASKS[chat_id]['running'] = False
        await asyncio.sleep(0.2)
        for w in PFP_TASKS[chat_id].get('workers', []):
            w.cancel()
        del PFP_TASKS[chat_id]
        if chat_id in PFP_MEDIA:
            del PFP_MEDIA[chat_id]
        await update.message.reply_text(ast_ok("PFP Loop Stopped"))
    else:
        await update.message.reply_text(ast_info("Nothing Active · PFP"))


# ═══════════════ 𝐒𝐏𝐀𝐌 ═══════════════
TG_MAX_LEN = 4096

SPAM1_SYMBOLS = ["𒈙"]
SPAM1_EMOJIS = ["☢️", "🩷", "🔥", "🦈", "👾", "❄️", "💠", "🀄", "🧃", "☀️", "🫧", "🥁", "💀", "🖤", "🌟"]
SPAM1_END = ["ᑕʜꪊD"]
SPAM1_TASKS = {}
SPAM1_TARGETS = {}


def build_spam1_payload(target=""):
    sym = random.choice(SPAM1_SYMBOLS)
    em = random.choice(SPAM1_EMOJIS)
    end = random.choice(SPAM1_END)
    prefix = f"{target} " if target else ""
    unit = f"{prefix}{sym * 9}{em}"
    reps = (TG_MAX_LEN // len(unit)) + 1
    payload = (unit * reps)[:TG_MAX_LEN - len(end) - 2]
    return payload + " " + end


async def spam1_worker(bot_app, chat_id, task_id):
    sem = get_sem(id(bot_app))
    while SPAM1_TASKS.get(task_id, {}).get('running', False):
        try:
            target = SPAM1_TARGETS.get(chat_id, "")
            payload = build_spam1_payload(target)
            async with sem:
                await bot_app.bot.send_message(chat_id=chat_id, text=payload)
            GLOBAL_STATS["messages_sent"] += 1
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(int(e.retry_after) + RETRY_AFTER_BUFFER)
        except Exception as e:
            err = str(e).lower()
            if "flood" in err:
                m = re.search(r'retry in (\d+)', err)
                await asyncio.sleep(int(m.group(1)) + 2 if m else 30)
            else:
                await asyncio.sleep(0.03)


async def b_spam1(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not acquire_reply_lock("spam1", update.effective_chat.id):
        return
    chat_id = update.effective_chat.id
    if not ALL_BOT_APPS:
        await update.message.reply_text(ast_err("No Bots Active"))
        return
    target = pick_target(update, context, default="")
    if chat_id in SPAM1_TASKS and SPAM1_TASKS[chat_id].get('running'):
        SPAM1_TASKS[chat_id]['running'] = False
        await asyncio.sleep(0.2)
        for w in SPAM1_TASKS[chat_id].get('workers', []):
            w.cancel()
    SPAM1_TASKS[chat_id] = {'running': True, 'workers': []}
    SPAM1_TARGETS[chat_id] = target
    workers = 0
    for bot_app in list(ALL_BOT_APPS):
        task = asyncio.create_task(spam1_worker(bot_app, chat_id, chat_id))
        SPAM1_TASKS[chat_id]['workers'].append(task)
        workers += 1
    await update.message.reply_text(
        ast_ok(f"Spam1 Started · {workers} bots · {target or 'no target'} · /stopspam1")
    )


async def b_stopspam1(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not acquire_reply_lock("stopspam1", update.effective_chat.id):
        return
    chat_id = update.effective_chat.id
    if chat_id in SPAM1_TASKS and SPAM1_TASKS[chat_id].get('running'):
        SPAM1_TASKS[chat_id]['running'] = False
        await asyncio.sleep(0.2)
        for w in SPAM1_TASKS[chat_id].get('workers', []):
            w.cancel()
        del SPAM1_TASKS[chat_id]
        if chat_id in SPAM1_TARGETS:
            del SPAM1_TARGETS[chat_id]
        await update.message.reply_text(ast_ok("Spam1 Stopped"))
    else:
        await update.message.reply_text(ast_info("Nothing Active · Spam1"))


SPAM_TASKS = {}
SPAM_TARGETS = {}


def build_custom_spam_payload(base_text):
    if not base_text.strip():
        base_text = "SYLAS"
    unit = f"{base_text} "
    reps = (TG_MAX_LEN // len(unit)) + 1
    return (unit * reps)[:TG_MAX_LEN]


async def custom_spam_worker(bot_app, chat_id, task_id):
    sem = get_sem(id(bot_app))
    while SPAM_TASKS.get(task_id, {}).get('running', False):
        try:
            base = SPAM_TARGETS.get(chat_id, "SYLAS")
            payload = build_custom_spam_payload(base)
            async with sem:
                await bot_app.bot.send_message(chat_id=chat_id, text=payload)
            GLOBAL_STATS["messages_sent"] += 1
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(int(e.retry_after) + RETRY_AFTER_BUFFER)
        except Exception as e:
            err = str(e).lower()
            if "flood" in err:
                m = re.search(r'retry in (\d+)', err)
                await asyncio.sleep(int(m.group(1)) + 2 if m else 30)
            else:
                await asyncio.sleep(0.03)


async def b_spam(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not acquire_reply_lock("spam", update.effective_chat.id):
        return
    chat_id = update.effective_chat.id
    if not ALL_BOT_APPS:
        await update.message.reply_text(ast_err("No Bots Active"))
        return
    if not context.args:
        await update.message.reply_text(ast_info("Usage · /spam <text>"))
        return
    base = " ".join(context.args)
    if chat_id in SPAM_TASKS and SPAM_TASKS[chat_id].get('running'):
        SPAM_TASKS[chat_id]['running'] = False
        await asyncio.sleep(0.2)
        for w in SPAM_TASKS[chat_id].get('workers', []):
            w.cancel()
    SPAM_TASKS[chat_id] = {'running': True, 'workers': []}
    SPAM_TARGETS[chat_id] = base
    workers = 0
    for bot_app in list(ALL_BOT_APPS):
        task = asyncio.create_task(custom_spam_worker(bot_app, chat_id, chat_id))
        SPAM_TASKS[chat_id]['workers'].append(task)
        workers += 1
    await update.message.reply_text(
        ast_ok(f"Spam Started · {workers} bots · /stopspam")
    )


async def b_stopspam(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not acquire_reply_lock("stopspam", update.effective_chat.id):
        return
    chat_id = update.effective_chat.id
    if chat_id in SPAM_TASKS and SPAM_TASKS[chat_id].get('running'):
        SPAM_TASKS[chat_id]['running'] = False
        await asyncio.sleep(0.2)
        for w in SPAM_TASKS[chat_id].get('workers', []):
            w.cancel()
        del SPAM_TASKS[chat_id]
        if chat_id in SPAM_TARGETS:
            del SPAM_TARGETS[chat_id]
        await update.message.reply_text(ast_ok("Spam Stopped"))
    else:
        await update.message.reply_text(ast_info("Nothing Active · Spam"))


DSPAM_TASKS = {}
DSPAM_TARGETS = {}


def build_dspam_payload(target=""):
    t = target if target else "Chutiya"
    unit = f"{t} 𝐃ʜᴀᴍ 🥁𝐃ʜᴀᴍ 🥁𝐂ᴜᴅɪ 𝐂ᴜᴅɪ {t} 𝐓ᴇʀɪ 𝐌ᴀ ᴄᴜᴅɪ🥁🥁 "
    reps = (TG_MAX_LEN // len(unit)) + 1
    return (unit * reps)[:TG_MAX_LEN]


async def dspam_worker(bot_app, chat_id, task_id):
    sem = get_sem(id(bot_app))
    while DSPAM_TASKS.get(task_id, {}).get('running', False):
        try:
            target = DSPAM_TARGETS.get(chat_id, "")
            payload = build_dspam_payload(target)
            async with sem:
                await bot_app.bot.send_message(chat_id=chat_id, text=payload)
            GLOBAL_STATS["messages_sent"] += 1
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(int(e.retry_after) + RETRY_AFTER_BUFFER)
        except Exception as e:
            err = str(e).lower()
            if "flood" in err:
                m = re.search(r'retry in (\d+)', err)
                await asyncio.sleep(int(m.group(1)) + 2 if m else 30)
            else:
                await asyncio.sleep(0.03)


async def b_dspam(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not acquire_reply_lock("dspam", update.effective_chat.id):
        return
    chat_id = update.effective_chat.id
    if not ALL_BOT_APPS:
        await update.message.reply_text(ast_err("No Bots Active"))
        return
    target = pick_target(update, context, default="")
    if chat_id in DSPAM_TASKS and DSPAM_TASKS[chat_id].get('running'):
        DSPAM_TASKS[chat_id]['running'] = False
        await asyncio.sleep(0.2)
        for w in DSPAM_TASKS[chat_id].get('workers', []):
            w.cancel()
    DSPAM_TASKS[chat_id] = {'running': True, 'workers': []}
    DSPAM_TARGETS[chat_id] = target
    workers = 0
    for bot_app in list(ALL_BOT_APPS):
        task = asyncio.create_task(dspam_worker(bot_app, chat_id, chat_id))
        DSPAM_TASKS[chat_id]['workers'].append(task)
        workers += 1
    await update.message.reply_text(
        ast_ok(f"DSpam Started · {workers} bots · {target or 'no target'} · /stopdspam")
    )


async def b_stopdspam(update, context):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(UNSUDO_MSG)
        return
    if not acquire_reply_lock("stopdspam", update.effective_chat.id):
        return
    chat_id = update.effective_chat.id
    if chat_id in DSPAM_TASKS and DSPAM_TASKS[chat_id].get('running'):
        DSPAM_TASKS[chat_id]['running'] = False
        await asyncio.sleep(0.2)
        for w in DSPAM_TASKS[chat_id].get('workers', []):
            w.cancel()
        del DSPAM_TASKS[chat_id]
        if chat_id in DSPAM_TARGETS:
            del DSPAM_TARGETS[chat_id]
        await update.message.reply_text(ast_ok("DSpam Stopped"))
    else:
        await update.message.reply_text(ast_info("Nothing Active · DSpam"))


# ═══════════════ 𝐒𝐓𝐀𝐓𝐔𝐒 𝐇𝐀𝐍𝐃𝐋𝐄𝐑 ═══════════════
async def status_handler(update, context):
    if not update.my_chat_member:
        return
    chat = update.my_chat_member.chat
    old = update.my_chat_member.old_chat_member.status
    new = update.my_chat_member.new_chat_member.status
    bot = await context.bot.get_me()

    if new in ["left", "kicked"] and old in ["member", "administrator"]:
        action = "KICKED" if new == "kicked" else "LEFT"
        try:
            await context.bot.send_message(
                OWNER_ID,
                ast_warn(f"Bot {action} · @{bot.username} · {chat.title}")
            )
        except Exception:
            pass
    elif new == "member" and old not in ["member", "administrator"]:
        try:
            await context.bot.send_message(
                OWNER_ID,
                ast_ok(f"Bot Added · @{bot.username} · {chat.title}")
            )
        except Exception:
            pass

        lock_key = f"added:{chat.id}"
        now = time.time()
        if lock_key in CMD_REPLY_LOCK and now - CMD_REPLY_LOCK[lock_key] < 10:
            return
        CMD_REPLY_LOCK[lock_key] = now

        welcome = BOT_WELCOME.format(status="👤 NORMAL USER — /menu to begin")
        try:
            await context.bot.send_message(chat.id, welcome)
        except Exception:
            pass


# ═══════════════ 𝐌𝐄𝐒𝐒𝐀𝐆𝐄 𝐂𝐎𝐋𝐋𝐄𝐂𝐓𝐎𝐑 ═══════════════
async def msg_collector(update, context):
    if not update.message:
        return
    if update.message.text and update.message.text.startswith('/'):
        return
    chat_id = update.effective_chat.id

    has_reply = chat_id in REPLY_TASKS and REPLY_TASKS[chat_id].get('running')
    has_rr = chat_id in RR_TASKS and RR_TASKS[chat_id].get('running')
    has_react = chat_id in REACT_CHATS

    if not (has_reply or has_rr or has_react):
        return

    msg_id = update.message.message_id

    if has_react:
        try:
            mode = REACT_MODE.get(chat_id, "single")
            if mode == "all":
                emoji_to_set = random.choice(REACT_ALL_POOL)
            else:
                emoji_to_set = REACT_EMOJI.get(chat_id, "🤣")
            try:
                await update.message.set_reaction(reaction=emoji_to_set)
            except Exception:
                try:
                    from telegram import ReactionTypeEmoji
                    await update.message.set_reaction(
                        reaction=[ReactionTypeEmoji(emoji=emoji_to_set)]
                    )
                except Exception as e2:
                    print(f"[REACT] {type(e2).__name__}: {e2}")
        except Exception as e:
            print(f"[REACT-OUTER] {type(e).__name__}: {e}")

    if not update.message.text:
        return

    sender = update.message.from_user
    sender_id = sender.id if sender else None

    if has_reply:
        if chat_id not in PENDING_REPLIES:
            PENDING_REPLIES[chat_id] = []
        PENDING_REPLIES[chat_id].append(msg_id)

    if has_rr and sender_id and sender_id == RR_TARGETS.get(chat_id):
        if chat_id not in PENDING_RR:
            PENDING_RR[chat_id] = []
        PENDING_RR[chat_id].append(msg_id)


# ═══════════════ 𝐂𝐀𝐋𝐋𝐁𝐀𝐂𝐊 ═══════════════
def _main_welcome_kb():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("◈ " + mf("Commands"), callback_data="sylas_cmds"),
            InlineKeyboardButton("◈ " + mf("Status"), callback_data="sylas_status"),
        ],
        [
            InlineKeyboardButton("◈ " + mf("Owner"), callback_data="sylas_owner"),
            InlineKeyboardButton("◈ " + mf("About"), callback_data="sylas_about"),
        ],
    ])


def _main_welcome_text(uid, name):
    status = "👑 " + mf("SUDO") if is_admin(uid) else "👤 " + mf("USER")
    return (
        "╭────────────── 𓂃𓈒𓏸 ──────────────╮\n\n"
        "              " + SYLAS_DISPLAY + "\n\n"
        "        " + mf("beyond the ordinary") + "\n\n"
        "     ─────────────────────────\n\n"
       f"        " + mf("Welcome back") + ",\n"
       f"        " + mf(name) + "  ·  " + status + "\n\n"
        "     ─────────────────────────\n\n"
        "        " + mf("System") + " · " + mf("ONLINE") + "\n\n"
        "     ─────────────────────────\n\n"
        "        " + SYLAS_DISPLAY + "\n"
        "        " + MADE_BY + "\n\n"
        "╰────────────── 𓂃𓈒𓏸 ──────────────╯"
    )


async def cb_handler(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data

    back_row = [InlineKeyboardButton("◂ " + mf("Back"), callback_data="sylas_back")]
    back_kb = InlineKeyboardMarkup([back_row])

    if data == "sylas_back":
        uid = update.effective_user.id
        name = update.effective_user.first_name or "User"
        try:
            await query.edit_message_text(
                _main_welcome_text(uid, name),
                reply_markup=_main_welcome_kb()
            )
        except Exception:
            pass
        return

    if data == "sylas_cmds":
        text = (
            "╭────────────── 𓂃𓈒𓏸 ──────────────╮\n\n"
            "        📜 " + mf("COMMANDS") + "\n\n"
            "     ─────────────────────────\n\n"
            "        ⟡ " + mf("NC") + "\n"
            "          › /nc  /nc1  /sylasnc  /sync  /botnc\n"
            "          › /gnc  /lnc  /rnc  /sylasnc2\n\n"
            "        ⟡ " + mf("SPAM") + "\n"
            "          › /spam  /spam1  /dspam  /picspam\n\n"
            "        ⟡ " + mf("PFP") + "\n"
            "          › /pfp\n\n"
            "        ⟡ " + mf("Tools") + "\n"
            "          › /lock  /unlock  /purge  /purgeall\n"
            "          › /optimize  /stats\n\n"
            "        " + mf("Prefixes") + " · /  .  !  ~\n\n"
            "╰────────────── 𓂃𓈒𓏸 ──────────────╯"
        )
        try:
            await query.edit_message_text(text, reply_markup=back_kb)
        except Exception:
            pass

    elif data == "sylas_status":
        uptime_secs = int(time.time() - GLOBAL_STATS["start_time"])
        h, rem = divmod(uptime_secs, 3600)
        mn, s = divmod(rem, 60)
        d, h = divmod(h, 24)
        parts = []
        if d:
            parts.append(f"{d}d")
        if h:
            parts.append(f"{h}h")
        if mn:
            parts.append(f"{mn}m")
        parts.append(f"{s}s")
        text = (
            "╭────────────── 𓂃𓈒𓏸 ──────────────╮\n\n"
            "        📊 " + mf("STATUS") + "\n\n"
            "     ─────────────────────────\n\n"
           f"        ⏱️  " + mf("Uptime") + f" · {' '.join(parts)}\n"
           f"        🤖  " + mf("Bots") + f" · {len(ALL_BOT_APPS)}\n"
           f"        💬  " + mf("Messages") + f" · {GLOBAL_STATS['messages_sent']}\n"
           f"        ↩️  " + mf("Replies") + f" · {GLOBAL_STATS['replies_sent']}\n\n"
            "╰────────────── 𓂃𓈒𓏸 ──────────────╯"
        )
        try:
            await query.edit_message_text(text, reply_markup=back_kb)
        except Exception:
            pass

    elif data == "sylas_owner":
        uid = update.effective_user.id
        text = (
            "╭────────────── 𓂃𓈒𓏸 ──────────────╮\n\n"
            "        👑 " + mf("OWNER") + "\n\n"
            "     ─────────────────────────\n\n"
           f"        " + mf("Owner ID") + f" · `{OWNER_ID}`\n"
           f"        " + mf("Your ID") + f" · `{uid}`\n\n"
           f"        " + mf("Sudo") + f" · {len(ADMIN_IDS)} users\n\n"
            "╰────────────── 𓂃𓈒𓏸 ──────────────╯"
        )
        try:
            await query.edit_message_text(text, reply_markup=back_kb)
        except Exception:
            pass

    elif data == "sylas_about":
        text = (
            "╭────────────── 𓂃𓈒𓏸 ──────────────╮\n\n"
            "        ℹ️ " + mf("ABOUT") + "\n\n"
            "     ─────────────────────────\n\n"
            "        " + mf("SYLAS GOD MOD") + "\n\n"
            "        " + mf("Multi-bot Telegram") + "\n"
            "        " + mf("management framework") + "\n\n"
            "        " + MADE_BY + "\n\n"
            "╰────────────── 𓂃𓈒𓏸 ──────────────╯"
        )
        try:
            await query.edit_message_text(text, reply_markup=back_kb)
        except Exception:
            pass


# ═══════════════ 𝐂𝐌𝐃 𝐌𝐀𝐏 ═══════════════
CMD_MAP = {
    "start": b_start,
    "menu": b_menu,
    "ping": b_ping,
    "tts": b_tts,
    "ttsja": b_ttsja,
    "mute": b_mute,
    "unmute": b_unmute,
    "admin": b_admin,
    "adminoff": b_adminoff,
    "legarib": b_legarib,
    "hatgarib": b_hatgarib,
    "garibokilist": b_garibokilist,
    "addhost": b_addhost,
    "mybots": b_mybots,
    "removehost": b_removehost,
    "hostlist": b_hostlist,
    "reply": b_reply,
    "stopreply": b_stopreply,
    "rr": b_rr,
    "stoprr": b_stoprr,
    "delay": b_delay,
    "purge": b_purge,
    "purgeall": b_purgeall,
    "lock": b_lock,
    "unlock": b_unlock,
    "leave": b_leave,
    "leaveall": b_leaveall,
    "stopall": b_stopall,
    "uptime": b_uptime,
    "status": b_status,
    "stats": b_stats,
    "react": b_react,
    "ereact": b_ereact,
    "optimize": b_optimize,
    "nc": b_nc,
    "stopnc": b_stopnc,
    "nc1": b_nc1,
    "stopnc1": b_stopnc1,
    "sylasnc": b_sylasnc,
    "stopsylasnc": b_stopsylasnc,
    "sync": b_sync,
    "stopsync": b_stopsync,
    "botnc": b_botnc,
    "stopbotnc": b_stopbotnc,
    "gnc": b_gnc,
    "stopgnc": b_stopgnc,
    "lnc": b_lnc,
    "stoplnc": b_stoplnc,
    "sylasnc2": b_sylasnc2,
    "stopsylasnc2": b_stopsylasnc2,
    "rnc": b_rnc,
    "stoprnc": b_stoprnc,
    "spam": b_spam,
    "stopspam": b_stopspam,
    "spam1": b_spam1,
    "stopspam1": b_stopspam1,
    "dspam": b_dspam,
    "stopdspam": b_stopdspam,
    "picspam": b_picspam,
    "stoppicspam": b_stoppicspam,
    "pfp": b_pfp,
    "stoppfp": b_stoppfp,
}


async def prefix_handler(update, context):
    if not update.message or not update.message.text:
        return
    text = update.message.text
    if not text:
        return
    prefix = text[0]
    if prefix in ['.', '!', '~']:
        parts = text[1:].split()
        if not parts:
            return
        command = parts[0].lower()
        context.args = parts[1:]
        handler = CMD_MAP.get(command)
        if handler:
            try:
                await handler(update, context)
            except Exception as e:
                print(f"[PREFIX] {command} error: {e}")


def attach_all_handlers(app):
    for cmd, handler in CMD_MAP.items():
        app.add_handler(CommandHandler(cmd, handler))
    app.add_handler(CallbackQueryHandler(cb_handler, pattern="^sylas_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, prefix_handler))
    app.add_handler(ChatMemberHandler(status_handler, ChatMemberHandler.MY_CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, msg_collector))


# ═══════════════ 𝐁𝐎𝐓 𝐑𝐔𝐍𝐍𝐄𝐑 ═══════════════
async def run_bot(token, bot_num, proxy_url=None, hosted=False):
    global PRIMARY_BOT_ID
    if not hosted:
        await asyncio.sleep(bot_num * 1.5)

    if proxy_url:
        request = HTTPXRequest(
            proxy_url=proxy_url,
            connection_pool_size=POOL_SIZE,
            connect_timeout=CONNECT_TIMEOUT,
            read_timeout=READ_TIMEOUT,
        )
    else:
        request = HTTPXRequest(
            connection_pool_size=POOL_SIZE,
            connect_timeout=CONNECT_TIMEOUT,
            read_timeout=READ_TIMEOUT,
        )

    retry_count = 0

    while True:
        builder = Application.builder().token(token).request(request)
        app = builder.build()
        attach_all_handlers(app)

        try:
            await app.initialize()
            await app.start()
            await app.updater.start_polling(drop_pending_updates=True)
            bot = await app.bot.get_me()
            tag = "Hosted" if hosted else "Main"
            proxy_info = " [Proxy]" if proxy_url else ""
            print(f"  ✅ [{tag}] Bot {bot_num}: @{bot.username}{proxy_info}")

            ALL_BOT_APPS.add(app)
            if hosted:
                HOSTED_APPS.add(app)

            if PRIMARY_BOT_ID is None:
                PRIMARY_BOT_ID = bot.id
                print(f"  ⭐ Primary bot set: @{bot.username} (id={bot.id})")

            retry_count = 0
            while True:
                await asyncio.sleep(3600)

        except TelegramConflict:
            try:
                await app.updater.stop()
                await app.stop()
                await app.shutdown()
            except Exception:
                pass
            await asyncio.sleep(5)
            continue

        except (NetworkError, TimedOut) as e:
            try:
                await app.updater.stop()
                await app.stop()
                await app.shutdown()
            except Exception:
                pass
            retry_count += 1
            wait = min(retry_count * 5, 60)
            print(f"  ⚠️ [{tag}] Bot {bot_num} NetworkError · retry in {wait}s · {e}")
            await asyncio.sleep(wait)
            if retry_count > 10:
                print(f"  ❌ [{tag}] Bot {bot_num} giving up after 10 retries")
                break
            continue

        except Exception as e:
            if "flood" in str(e).lower():
                m = re.search(r'retry in (\d+)', str(e).lower())
                try:
                    await app.updater.stop()
                    await app.stop()
                    await app.shutdown()
                except Exception:
                    pass
                await asyncio.sleep(int(m.group(1)) + 2 if m else 30)
                continue
            print(f"  ❌ [{tag}] Bot {bot_num}: {e}")
            logger.warning(f"Bot {bot_num} crashed: {e}")
            break

        finally:
            ALL_BOT_APPS.discard(app)
            HOSTED_APPS.discard(app)
            try:
                await app.updater.stop()
                await app.stop()
                await app.shutdown()
            except Exception:
                pass

        break


# ═══════════════ 𝐌𝐀𝐈𝐍 ═══════════════
async def main():
    print(short_ok(f"{VERSION} starting · MAX SPEED"))
    asyncio.create_task(keepalive_server())

    for uid, bots in HOSTED_BOTS.items():
        for bot in bots:
            asyncio.create_task(
                run_bot(bot['token'], bot['bot_num'], get_proxy(bot['bot_num']), hosted=True)
            )

    session = await get_session()
    print(short_info("Starting userbot"))
    ub = TelegramClient(StringSession(session), API_ID, API_HASH)
    ub.add_event_handler(ub_bots)
    await ub.start()
    me = await ub.get_me()
    print(short_ok(f"Userbot · {me.first_name}"))

    print(short_info(f"Launching {len(BOT_TOKENS)} bots"))
    bot_tasks = [
        asyncio.create_task(run_bot(t, i, get_proxy(i)))
        for i, t in enumerate(BOT_TOKENS, 1)
    ]

    print(short_ok("READY · /menu  .menu  !menu  ~menu"))

    try:
        await asyncio.gather(*bot_tasks)
    except KeyboardInterrupt:
        pass

    print(short_warn("Shutting down"))
    for app in list(ALL_BOT_APPS):
        try:
            await app.updater.stop()
            await app.stop()
            await app.shutdown()
        except Exception:
            pass
    try:
        await ub.disconnect()
    except Exception:
        pass
    print(short_ok("Done"))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋")