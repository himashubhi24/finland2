#(©)Codexbotz

import asyncio
import random

from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait

from bot import Bot
from config import CHANNEL_ID, DISABLE_CHANNEL_BUTTON, ADMINS, UPLOAD_ADMINS, LOG_CHANNEL
from helper_func import encode


AUTO_BATCH_WAIT = 60
AUTO_BATCHES = {}
AUTO_BATCH_TASKS = {}
AUTO_BATCH_LOCK = asyncio.Lock()


async def finish_auto_batch(client: Client, user_id: int):
    try:
        await asyncio.sleep(AUTO_BATCH_WAIT)
    except asyncio.CancelledError:
        return

    batch = AUTO_BATCHES.pop(user_id, None)
    AUTO_BATCH_TASKS.pop(user_id, None)

    if not batch:
        return

    ids = batch["ids"]
    reply_msg = batch["reply_msg"]

    first_id = min(ids)
    last_id = max(ids)

    string = f"get-{first_id}-{last_id}"
    base64_string = await encode(string)

    link = f"https://t.me/{client.username}?start={base64_string}"

    try:
        await client.send_message(
            chat_id=LOG_CHANNEL,
            text=f"""
📤 Upload Admin Log

👤 User: {reply_msg.chat.first_name if reply_msg.chat else user_id}
🆔 User ID: <code>{user_id}</code>

📂 Files: {len(ids)}
🔗 Link: {link}
"""
        )
    except Exception as e:
        print("UPLOAD_LOG_ERROR:", e)

    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🔁 Share URL",
                    url=f"https://telegram.me/share/url?url={link}"
                )
            ]
        ]
    )

    text = f"""
🔗 Your Link is Ready 👇

Link is locked 🔒
{link}

📂 Total Files : {len(ids)}
💎 Upgrade to Premium for accessing all links
"""

    try:
        await reply_msg.edit(
            text,
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
    except Exception as e:
        print("AUTO_BATCH_EDIT_ERROR:", e)
        try:
            await client.send_message(
                user_id,
                text,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
        except Exception as e2:
            print("AUTO_BATCH_SEND_ERROR:", e2)


@Bot.on_message(
    filters.private
    & filters.user(ADMINS + UPLOAD_ADMINS)
    & ~filters.command(['start', 'users', 'broadcast', 'stats', 'premiumusers', 'payments', 'addpremium', 'removepremium', 'adminpremium', 'admin'])
)
async def channel_post(client: Client, message: Message):

    user_id = message.from_user.id

    async with AUTO_BATCH_LOCK:
        if user_id not in AUTO_BATCHES:
            reply_text = await message.reply_text(
                f"⏳ Auto batch started...\n\nSend all videos/files now.\nI will create one batch link after {AUTO_BATCH_WAIT} seconds of last file.",
                quote=True
            )

            AUTO_BATCHES[user_id] = {
                "ids": [],
                "reply_msg": reply_text
            }

    try:
        post_message = await message.copy(
            chat_id=client.db_channel.id,
            disable_notification=True
        )

    except FloodWait as e:
        await asyncio.sleep(e.value)

        post_message = await message.copy(
            chat_id=client.db_channel.id,
            disable_notification=True
        )

    except Exception as e:
        print(e)

        try:
            await AUTO_BATCHES[user_id]["reply_msg"].edit_text(
                "Something went Wrong..!"
            )
        except Exception:
            pass

        return

    converted_id = post_message.id * abs(client.db_channel.id)
    AUTO_BATCHES[user_id]["ids"].append(converted_id)

    old_task = AUTO_BATCH_TASKS.get(user_id)
    if old_task:
        old_task.cancel()

    AUTO_BATCH_TASKS[user_id] = asyncio.create_task(
        finish_auto_batch(client, user_id)
    )


@Bot.on_message(
    filters.channel
    & filters.incoming
    & filters.chat(CHANNEL_ID)
)
async def new_post(client: Client, message: Message):

    if DISABLE_CHANNEL_BUTTON:
        return

    converted_id = message.id * abs(client.db_channel.id)

    string = f"get-{converted_id}"

    base64_string = await encode(string)

    link = f"https://t.me/{client.username}?start={base64_string}"

    try:
        await client.send_message(
            chat_id=LOG_CHANNEL,
            text=f"""
📤 Upload Admin Log

👤 User: {reply_msg.chat.first_name if reply_msg.chat else user_id}
🆔 User ID: <code>{user_id}</code>

📂 Files: {len(ids)}
🔗 Link: {link}
"""
        )
    except Exception as e:
        print("UPLOAD_LOG_ERROR:", e)

    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🔁 Share URL",
                    url=f"https://telegram.me/share/url?url={link}"
                )
            ]
        ]
    )

    try:
        await message.edit_reply_markup(reply_markup)

    except FloodWait as e:
        await asyncio.sleep(e.value)
        await message.edit_reply_markup(reply_markup)

    except Exception:
        pass
