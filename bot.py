import os
import re
import asyncio
from telegram import Bot, Update, ChatPermissions
from telegram.ext import Application, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN", "PASTE_YOUR_BOT_TOKEN_HERE")
CHAT_ID = os.getenv("CHAT_ID", "PASTE_GROUP_ID_HERE")
GROUP_LINK = os.getenv("GROUP_LINK", "https://t.me/yourgroup")
PHOTO_URL = os.getenv("PHOTO_URL", "PASTE_PUBLIC_PHOTO_URL_HERE")

# 24 hours = 86400 seconds
MUTE_SECONDS = 86400

# Add/adjust words commonly used in scam/fraud messages.
FRAUD_WORDS = [
    "fraud", "scam", "fake", "phishing", "otp", "verification code",
    "upi pin", "cvv", "bank password", "account blocked", "claim prize",
    "lottery", "free money", "investment guaranteed", "double your money",
    "send money", "pay now", "urgent payment"
]

URL_RE = re.compile(r"(https?://|www\.|t\.me/|telegram\.me/)", re.I)

def contains_link(text: str) -> bool:
    return bool(URL_RE.search(text or ""))

def looks_like_fraud(text: str) -> bool:
    t = (text or "").lower()
    return any(word in t for word in FRAUD_WORDS)

async def mute_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or not update.effective_user:
        return
    if update.effective_chat.type not in ("group", "supergroup"):
        return

    user = update.effective_user

    # Never punish group admins/owners.
    member = await context.bot.get_chat_member(update.effective_chat.id, user.id)
    if member.status in ("administrator", "creator"):
        return

    until_date = update.message.date.timestamp() + MUTE_SECONDS
    permissions = ChatPermissions(can_send_messages=False)

    try:
        await context.bot.restrict_chat_member(
            chat_id=update.effective_chat.id,
            user_id=user.id,
            permissions=permissions,
            until_date=int(until_date),
        )
    except Exception as e:
        print("Could not mute:", e)

async def moderate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if not msg:
        return

    text = msg.text or msg.caption or ""

    # Telegram marks forwarded messages; also check text/caption.
    is_forwarded = bool(
        getattr(msg, "forward_origin", None)
        or getattr(msg, "forward_from", None)
        or getattr(msg, "forward_from_chat", None)
    )

    # Block links, suspicious forwarded content, and obvious scam/fraud text.
    suspicious = contains_link(text) or looks_like_fraud(text) or (
        is_forwarded and (contains_link(text) or looks_like_fraud(text))
    )

    if not suspicious:
        return

    try:
        await msg.delete()
    except Exception as e:
        print("Could not delete:", e)

    await mute_user(update, context)

async def hourly_post(context: ContextTypes.DEFAULT_TYPE):
    keyboard = {
        "inline_keyboard": [[
            {"text": "👉 JOIN GROUP", "url": GROUP_LINK}
        ]]
    }

    try:
        await context.bot.send_photo(
            chat_id=CHAT_ID,
            photo=PHOTO_URL,
            caption="🔥 NEW GROUP 🔥\n\nNaye group me join karein 👇",
            reply_markup=keyboard,
        )
    except Exception as e:
        print("Hourly post error:", e)

async def post_init(application: Application):
    application.job_queue.run_repeating(hourly_post, interval=3600, first=0)

def main():
    app = Application.builder().token(TOKEN).post_init(post_init).build()
    app.add_handler(MessageHandler(filters.ALL & ~filters.StatusUpdate.ALL, moderate))
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
