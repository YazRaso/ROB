"""
This file is designed to listen to incoming messages, send them to backboard and save them to the db.
The program requires a bot token, you can get this through telegram using botfather
"""


import os
import httpx
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters,
)
import db

BOT_TOKEN = os.getenv("BOT_TOKEN")
SERVER_URL = "https://rob-production.up.railway.app/"

async def emit_telegram_event(client_id: str = None):
    """
    Emit a telegram event by calling the server's /events/emit endpoint.
    This notifies the frontend that telegram data has been received.
    """
    try:
        async with httpx.AsyncClient() as client:
            params = {"source": "telegram"}
            if client_id:
                params["client_id"] = client_id
            await client.post(f"{SERVER_URL}/events/emit", params=params)
    except Exception as e:
        print(f"Failed to emit telegram event: {e}")


# log_thread saves telegram messages with metadate to db, message is sent to backboard as consequence
async def log_thread(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or not msg.text:
        return
    chat = msg.chat
    sender = msg.from_user or msg.sender_chat
    thread = f"{sender.username}: {msg.text}"
    print(f"Message received from {sender.username}")
    client_id = db.get_client_with_bot_token(BOT_TOKEN)
    import requests
    parmas = {
        "client_id": client_id,
        "content": chat
    }
    requests.post(f"{SERVER_URL}/messages/send", params=params)



app = ApplicationBuilder().token(BOT_TOKEN).build()

# Bot will register and call log_thread upon receiving messages from telegram groups
app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, log_thread))

# App polls telegrams servers for new messages
app.run_polling()
