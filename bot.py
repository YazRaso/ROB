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

# log_thread saves telegram messages with metadate to db, message is sent to backboard as consequence
async def log_thread(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or not msg.text:
        return
    chat = msg.chat
    sender = msg.from_user or msg.sender_chat
    thread = f"{sender.username}: {msg.text}"
    db.create_thread(chat.id, msg.chat, thread)

app = ApplicationBuilder().token(BOT_TOKEN).build()

# Bot will register and call log_thread upon receiving messages from telegram groups
app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, log_thread))

# App polls telegrams servers for new messages
app.run_polling()
