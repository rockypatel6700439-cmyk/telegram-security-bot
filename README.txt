TELEGRAM GROUP MODERATION + HOURLY ANNOUNCEMENT BOT

FEATURES
- Sends group photo + announcement + JOIN GROUP button every 1 hour.
- Deletes messages containing links (http, www, t.me, telegram.me).
- Deletes obvious scam/fraud messages based on configurable keywords.
- Detects forwarded messages when Telegram exposes forward metadata.
- Mutes the sender for 24 hours after a suspicious message.
- Does not mute administrators/owners.
- Deletes the suspicious message before muting when permissions allow.

SETUP
1. Create a bot using @BotFather.
2. Add the bot to your group as an administrator.
3. Give it permission to delete messages and restrict/ban users.
4. Set environment variables:
   BOT_TOKEN
   CHAT_ID
   GROUP_LINK
   PHOTO_URL
5. Install:
   pip install -r requirements.txt
6. Run:
   python bot.py

IMPORTANT
- Keep BOT_TOKEN secret.
- The bot cannot reliably identify every fraud/scam message. The FRAUD_WORDS list can be expanded.
- Link filtering can be strict and may block legitimate links. Adjust contains_link() if needed.
- Telegram forwards are detected using available forward metadata; forwarded messages without suspicious content are not blocked by default.
- 24-hour mute means the user cannot send messages while the restriction is active, provided the bot has the required admin permission.
