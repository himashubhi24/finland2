#(©)CodeXBotz




import os
import asyncio
from datetime import datetime

from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated

from bot import Bot

from config import (
    ADMINS,
    FORCE_MSG,
    START_MSG,
    CUSTOM_CAPTION,
    DISABLE_CHANNEL_BUTTON,
    PROTECT_CONTENT,
    LOG_CHANNEL
)

from helper_func import subscribed, encode, decode, get_messages

from database.database import (
    check_premium_access,
    get_pending_plan,
    give_premium,
    remove_premium,
    add_user,
    del_user,
    full_userbase,
    present_user,
    update_user_activity,
    increase_files_count,
    add_file_stats,
    get_top_users,
    get_top_files,
    get_online_users,
    save_failed_log,
    get_failed_logs,
    get_premium_users,
    get_all_premium_users,
    ban_user,
    unban_user,
    is_banned,
    get_payment_logs,
    track_link_view,
    track_link_download,
    get_link_stats,
    get_upi_enabled
)

# ================= DAILY STATS ================= #

today_date = datetime.now().strftime("%Y-%m-%d")

daily_stats = {
    "date": today_date,
    "new_users": 0,
    "files_sent": 0
}


def reset_daily_stats():

    global daily_stats

    current = datetime.now().strftime("%Y-%m-%d")

    if daily_stats["date"] != current:

        daily_stats = {
            "date": current,
            "new_users": 0,
            "files_sent": 0
        }


# ================= AUTO DELETE ================= #

async def auto_delete(message, time=300):

    await asyncio.sleep(time)

    try:
        await message.delete()
    except:
        pass


async def send_premium_message(message):

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "✨ Get Premium",
                    callback_data="buy_access"
                )
            ],
            [
                InlineKeyboardButton(
                    "🎁 Refer & Earn",
                    callback_data="refer"
                )
            ]
        ]
    )

    text = """
🔒 Premium Access Required 🔓

This link requires premium access to view
files

Options to get Premium access:
1⃣ Purchase a premium plan
2⃣ Refer friends to earn free premium access

Upgrade now to unlock all content!
"""

    return await message.reply_text(
        text=text,
        reply_markup=buttons
    )


# ================= START COMMAND ================= #
@Bot.on_message(

    filters.command('start') &

    filters.private &

    subscribed

)
async def start_command(client: Client, message: Message):

    user = message.from_user

    user_id = user.id

    if await is_banned(user_id):
        return await message.reply_text("🚫 You are banned from using this bot.")

    reset_daily_stats()

    # ================= USER TRACKING ================= #

    if not await present_user(user_id):

        try:

            await add_user(user)

            daily_stats["new_users"] += 1

        except:
            pass

    else:

        try:
            await update_user_activity(user)
        except:
            pass

    text = message.text

    if text == "/start":
        premium = await check_premium_access(user_id)

        if premium:
            expiry_text = premium.strftime("%d %b %Y")
            badge = "💎 Premium User"
            expiry_line = f"⏳ Expires: {expiry_text}"
        else:
            badge = "🆓 Free User"
            expiry_line = "💎 Upgrade to Premium for protected files"

        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("✨ Get Premium", callback_data="buy_access")
                ]
            ]
        )

        return await message.reply_text(
            f"""
👤 {user.first_name}
{badge}
{expiry_line}
""",
            reply_markup=buttons
        )

    if text == "/start premium":

        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("7 Days ₹30", url="https://t.me/muthmuktsbot?start=plan7"),
                    InlineKeyboardButton("15 Days ₹40", url="https://t.me/muthmuktsbot?start=plan15")
                ],
                [
                    InlineKeyboardButton("30 Days ₹50", url="https://t.me/muthmuktsbot?start=plan30"),
                    InlineKeyboardButton("45 Days ₹80", url="https://t.me/muthmuktsbot?start=plan45")
                ]
            ]
        )

        return await message.reply_text(
            """
💎 Choose Your Premium Plan

✨ 7 Days — ₹30
✨ 15 Days — ₹40
✨ 30 Days — ₹50
✨ 45 Days — ₹80

Select a plan below 👇
""",
            reply_markup=buttons
        )

    if text == "/start plan7":

        return await message.reply_text(
            """
💳 Payment Details

Plan : 7 Days
Price : ₹30

Send payment screenshot after payment.
"""
        )

    if text == "/start plan15":

        return await message.reply_text(
            """
💳 Payment Details

Plan : 15 Days
Price : ₹40

Send payment screenshot after payment.
"""
        )

    if text == "/start plan30":

        return await message.reply_text(
            """
💳 Payment Details

Plan : 30 Days
Price : ₹50

Send payment screenshot after payment.
"""
        )

    if text == "/start plan45":

        return await message.reply_text(
            """
💳 Payment Details

Plan : 45 Days
Price : ₹80

Send payment screenshot after payment.
"""
        )

    # ================= FILE REQUEST ================= #

    if len(text.split()) > 1 and text.startswith("/start"):
        try:
            base64_string = text.split(" ", 1)[1]
        except:
            return

        try:
            string = await decode(base64_string)
        except:
            return

        argument = string.split("-")
        link_key = string

        try:
            await track_link_view(link_key, user_id)
        except:
            pass

        # MULTI FILE
        if len(argument) == 3:

            try:

                start = int(
                    int(argument[1]) / abs(client.db_channel.id)
                )

                end = int(
                    int(argument[2]) / abs(client.db_channel.id)
                )

            except:
                return

            if start <= end:

                ids = range(start, end + 1)

            else:

                ids = []

                i = start

                while True:

                    ids.append(i)

                    i -= 1

                    if i < end:
                        break

                # SINGLE FILE
        elif len(argument) == 2:

            try:

                ids = [
                    int(
                        int(argument[1]) / abs(client.db_channel.id)
                    )
                ]

            except:
                return

        else:
            return

        # ================= PREMIUM CHECK ================= #

        premium = await check_premium_access(user_id)

        if not premium:

            return await send_premium_message(message)

        temp_msg = await message.reply(
            "⚡ Processing files..."
        )

        try:

            messages = await get_messages(client, ids)

        except Exception as e:

            await save_failed_log(
                user_id,
                str(e)
            )

            await temp_msg.edit(
                "❌ Something went wrong."
            )

            return

        await temp_msg.delete()

        try:
            await track_link_download(link_key, len(ids))
        except:
            pass

        # ================= FAST FILE SEND ================= #

        for msg in messages:

            if bool(CUSTOM_CAPTION) and bool(msg.document):

                caption = CUSTOM_CAPTION.format(
                    previouscaption="" if not msg.caption else msg.caption.html,
                    filename=msg.document.file_name
                )

            else:

                caption = "" if not msg.caption else msg.caption.html

            if DISABLE_CHANNEL_BUTTON:

                reply_markup = msg.reply_markup

            else:

                reply_markup = None

            try:

                sent_msg = await msg.copy(
                    chat_id=message.from_user.id,
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup,
                    protect_content=PROTECT_CONTENT
                )

                # ================= STATS ================= #

                daily_stats["files_sent"] += 1

                try:
                    await increase_files_count(user_id)
                except:
                    pass

                try:

                    file_name = "Unknown File"

                    if msg.document:
                        file_name = msg.document.file_name

                    elif msg.video:
                        file_name = msg.video.file_name

                    elif msg.audio:
                        file_name = msg.audio.file_name

                    await add_file_stats(file_name)

                except:
                    pass

                # ================= AUTO DELETE ================= #

                asyncio.create_task(
                    auto_delete(sent_msg, 300)
                )

            except FloodWait as e:

                await asyncio.sleep(e.x)

                try:

                    sent_msg = await msg.copy(
                        chat_id=message.from_user.id,
                        caption=caption,
                        parse_mode=ParseMode.HTML,
                        reply_markup=reply_markup,
                        protect_content=PROTECT_CONTENT
                    )

                    daily_stats["files_sent"] += 1

                    asyncio.create_task(
                        auto_delete(sent_msg, 300)
                    )

                except Exception as err:

                    await save_failed_log(
                        user_id,
                        str(err)
                    )

            except Exception as err:

                await save_failed_log(
                    user_id,
                    str(err)
                )

        return

    # ================= NORMAL START ================= #

    else:

        reply_markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "😊 About Me",
                        callback_data="about"
                    ),

                    InlineKeyboardButton(
                        "🔒 Close",
                        callback_data="close"
                    )
                ]
            ]
        )

        await message.reply_text(
            text=START_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),

            reply_markup=reply_markup,
            disable_web_page_preview=True,
            quote=True
        )

        return


# ===================================================================================== #

WAIT_MSG = """<b>Processing ...</b>"""

REPLY_ERROR = """<code>Use this command as a replay to any telegram message with out any spaces.</code>"""

# ===================================================================================== #


# ================= FORCE SUB ================= #

@Bot.on_message(filters.command('start') & filters.private)
async def not_joined(client: Client, message: Message):

    buttons = [
        [
            InlineKeyboardButton(
                "Join Channel",
                url=client.invitelink
            )
        ]
    ]

    try:

        buttons.append(
            [
                InlineKeyboardButton(
                    text='Try Again',
                    url=f"https://t.me/{client.username}?start={message.command[1]}"
                )
            ]
        )

    except IndexError:
        pass

    await message.reply(
        text=FORCE_MSG.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name,
            username=None if not message.from_user.username else '@' + message.from_user.username,
            mention=message.from_user.mention,
            id=message.from_user.id
        ),

        reply_markup=InlineKeyboardMarkup(buttons),
        quote=True,
        disable_web_page_preview=True
    )


# ================= USERS ================= #

@Bot.on_message(filters.command('users') & filters.private & filters.user(ADMINS))
async def get_users(client: Bot, message: Message):

    msg = await client.send_message(
        chat_id=message.chat.id,
        text=WAIT_MSG
    )

    users = await full_userbase()

    await msg.edit(
        f"👥 Total Users In Database: {len(users)}"
    )


# ================= DAILY STATS ================= #

@Bot.on_message(filters.command('stats') & filters.private & filters.user(ADMINS))
async def daily_logs(client: Bot, message: Message):

    reset_daily_stats()

    online = await get_online_users()

    premium_users = await get_premium_users()

    total_users = len(
        await full_userbase()
    )

    text = f"""
📊 Finland Bot Stats

👥 Total Users: {total_users}

💎 Premium Users: {premium_users}

🟢 Online Users: {online}

👤 New Users Today: {daily_stats['new_users']}

📁 Files Sent Today: {daily_stats['files_sent']}
"""

    await message.reply_text(text)


# ================= TOP USERS ================= #

@Bot.on_message(filters.command('top') & filters.private)
async def top_users(client: Bot, message: Message):

    users = await get_top_users()

    text = "🏆 Top Active Users\n\n"

    count = 1

    for user in users:

        username = user.get("username")

        first_name = user.get("first_name")

        files_taken = user.get("files_taken", 0)

        if username:
            name = f"@{username}"
        else:
            name = first_name

        text += f"{count}. {name} — {files_taken} files\n"

        count += 1

    await message.reply_text(text)


# ================= TOP FILES ================= #

@Bot.on_message(filters.command('topfiles') & filters.private)
async def top_files(client: Bot, message: Message):

    files = await get_top_files()

    text = "🔥 Most Downloaded Files\n\n"

    count = 1

    for file in files:

        file_name = file.get("file_name")

        downloads = file.get("downloads", 0)

        text += f"{count}. {file_name} — {downloads} downloads\n"

        count += 1

    await message.reply_text(text)


# ================= ONLINE USERS ================= #

@Bot.on_message(filters.command('online') & filters.private)
async def online_users(client: Bot, message: Message):

    online = await get_online_users()

    await message.reply_text(
        f"🟢 Online Users: {online}"
    )


# ================= FAILED LOGS ================= #

@Bot.on_message(filters.command('errors') & filters.private)
async def failed_logs(client: Bot, message: Message):

    logs = await get_failed_logs()

    if not logs:

        return await message.reply_text(
            "✅ No Failed Logs Found"
        )

    text = "⚠️ Recent Failed Logs\n\n"

    for log in logs:

        text += (
            f"👤 User: {log.get('user_id')}\n"
            f"❌ Error: {log.get('error')}\n\n"
        )

    await message.reply_text(text[:4000])


# ================= BROADCAST ================= #

@Bot.on_message(filters.private & filters.command('broadcast') & filters.user(ADMINS))
async def send_text(client: Bot, message: Message):

    if message.reply_to_message:

        query = await full_userbase()

        broadcast_msg = message.reply_to_message

        total = 0
        successful = 0
        blocked = 0
        deleted = 0
        unsuccessful = 0

        pls_wait = await message.reply(
            "<i>Broadcasting Message... Please Wait</i>"
        )

        for chat_id in query:

            try:

                await broadcast_msg.copy(chat_id)

                successful += 1

            except FloodWait as e:

                await asyncio.sleep(e.x)

                try:

                    await broadcast_msg.copy(chat_id)

                    successful += 1

                except:
                    unsuccessful += 1

            except UserIsBlocked:

                await del_user(chat_id)

                blocked += 1

            except InputUserDeactivated:

                await del_user(chat_id)

                deleted += 1

            except:

                unsuccessful += 1

            total += 1

        status = f"""
<b><u>Broadcast Completed</u>

👥 Total Users: <code>{total}</code>

✅ Successful: <code>{successful}</code>

🚫 Blocked Users: <code>{blocked}</code>

❌ Deleted Accounts: <code>{deleted}</code>

⚠️ Unsuccessful: <code>{unsuccessful}</code></b>
"""

        return await pls_wait.edit(status)

    else:

        msg = await message.reply(REPLY_ERROR)

        await asyncio.sleep(8)

        await msg.delete()


# ================= PAYMENT SCREENSHOT ================= #

@Bot.on_message(filters.private & filters.photo)
async def payment_screenshot(client: Bot, message: Message):
    user = message.from_user

    print(f"PAYMENT_SCREENSHOT_RECEIVED user_id={user.id} username={user.username}", flush=True)

    plan = await get_pending_plan(user.id)
    days = int(plan["days"]) if plan else 30
    price = int(plan["price"]) if plan else 50

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user.id}_{days}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user.id}")
            ]
        ]
    )

    caption = f"""
💳 New Payment Screenshot

👤 User: {user.mention}
🆔 User ID: <code>{user.id}</code>
🔗 Username: @{user.username if user.username else 'None'}
📅 Plan: {days} Days
💰 Price: ₹{price}
"""

    try:
        await client.send_photo(
            chat_id=LOG_CHANNEL,
            photo=message.photo.file_id,
            caption=caption,
            reply_markup=buttons
        )
    except Exception as e:
        print(f"LOG_CHANNEL_SS_SEND_ERROR error={e}", flush=True)

    try:
        await message.delete()
    except:
        pass


@Bot.on_message(filters.command("addpremium") & filters.user(ADMINS))
async def add_premium_cmd(client, message):

    try:

        user_id = int(message.command[1])

        days = int(message.command[2])

    except:

        return await message.reply_text(
            "Usage:\n/addpremium user_id days"
        )

    expiry = await give_premium(
        user_id,
        days
    )

    await message.reply_text(
        f"""
✅ Premium Added

👤 User: <code>{user_id}</code>

📅 Days: <code>{days}</code>

⏳ Expiry:
<code>{expiry}</code>
"""
    )


@Bot.on_message(filters.command("removepremium") & filters.user(ADMINS))
async def remove_premium_cmd(client, message):

    try:

        user_id = int(message.command[1])

    except:

        return await message.reply_text(
            "Usage:\n/removepremium user_id"
        )

    await remove_premium(user_id)

    await message.reply_text(
        f"""
❌ Premium Removed

👤 User:
<code>{user_id}</code>
"""
    )
    # ================= MY PREMIUM ================= #


@Bot.on_message(filters.command("linkstats") & filters.private)
async def link_stats_cmd(client, message):
    stats = await get_link_stats(10)

    if not stats:
        return await message.reply_text("📊 No link stats found yet.")

    text = "📊 Link Stats\n\n"

    for i, item in enumerate(stats, 1):
        text += (
            f"{i}. `{item['_id']}`\n"
            f"👁 Views: {item.get('views', 0)}\n"
            f"👤 Unique Users: {item.get('unique_count', 0)}\n"
            f"⬇️ Downloads: {item.get('downloads', 0)}\n\n"
        )

    await message.reply_text(text)



@Bot.on_message(filters.command("premiumusers") & filters.private & filters.user(ADMINS))
async def premium_users_panel(client, message):
    users = await get_all_premium_users,
    ban_user,
    unban_user,
    is_banned()

    if not users:
        return await message.reply_text("💎 No premium users found.")

    text = "💎 Admin Premium Panel\n\n"

    for user in users[:30]:
        uid = user.get("_id")
        name = user.get("first_name", "Unknown")
        username = user.get("username")
        expiry = user.get("premium_expiry")

        expiry_text = expiry.strftime("%d %b %Y") if expiry else "N/A"
        uname = f"@{username}" if username else "No username"

        text += f"👤 {name} ({uname})\n🆔 <code>{uid}</code>\n⏳ Expires: {expiry_text}\n\n"

    await message.reply_text(text)


@Bot.on_message(filters.command("payments") & filters.private & filters.user(ADMINS))
async def payments_panel(client, message):
    logs = await get_payment_logs(20)

    if not logs:
        return await message.reply_text("💳 No payment history found.")

    text = "💳 Payment History\n\n"

    for item in logs:
        date = item.get("date")
        date_text = date.strftime("%d %b %Y %H:%M") if date else "N/A"

        text += (
            f"👤 User ID: <code>{item.get('user_id')}</code>\n"
            f"📅 Plan: {item.get('plan_days')} Days\n"
            f"💰 Amount: ₹{item.get('amount')}\n"
            f"📌 Status: {item.get('status')}\n"
            f"🕒 Date: {date_text}\n\n"
        )

    await message.reply_text(text)



@Bot.on_message(filters.command("adminpremium") & filters.private & filters.user(ADMINS))
async def admin_premium_buttons(client, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "Usage:\n/adminpremium USER_ID"
        )

    user_id = int(message.command[1])

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("➕ 7 Days", callback_data=f"manual_add_{user_id}_7"),
                InlineKeyboardButton("➕ 15 Days", callback_data=f"manual_add_{user_id}_15")
            ],
            [
                InlineKeyboardButton("➕ 30 Days", callback_data=f"manual_add_{user_id}_30"),
                InlineKeyboardButton("➕ 45 Days", callback_data=f"manual_add_{user_id}_45")
            ],
            [
                InlineKeyboardButton("❌ Remove Premium", callback_data=f"manual_remove_{user_id}")
            ]
        ]
    )

    await message.reply_text(
        f"💎 Premium Control Panel\n\nUser ID: <code>{user_id}</code>",
        reply_markup=buttons
    )



@Bot.on_message(filters.command("profile") & filters.private)
async def profile_cmd(client, message):
    user = message.from_user
    user_id = user.id

    premium = await check_premium_access(user_id)

    from database.database import user_data
    db_user = user_data.find_one({"_id": user_id}) or {}

    files_taken = db_user.get("files_taken", 0)

    if premium:
        status = "💎 Premium User"
        expiry = premium.strftime("%d %b %Y %H:%M")
    else:
        status = "🆓 Free User"
        expiry = "N/A"

    await message.reply_text(
        f"""
👤 {user.first_name}

🆔 User ID: <code>{user_id}</code>
🔗 Username: @{user.username if user.username else 'None'}

{status}
⏳ Expires: {expiry}

📥 Files Taken: {files_taken}
"""
    )


@Bot.on_message(filters.command("ban") & filters.private & filters.user(ADMINS))
async def ban_cmd(client, message):
    try:
        user_id = int(message.command[1])
    except:
        return await message.reply_text("Usage:\n/ban USER_ID")

    await ban_user(user_id)

    await message.reply_text(f"🚫 User banned: <code>{user_id}</code>")


@Bot.on_message(filters.command("unban") & filters.private & filters.user(ADMINS))
async def unban_cmd(client, message):
    try:
        user_id = int(message.command[1])
    except:
        return await message.reply_text("Usage:\n/unban USER_ID")

    await unban_user(user_id)

    await message.reply_text(f"✅ User unbanned: <code>{user_id}</code>")


@Bot.on_message(filters.command("mypremium") & filters.private)
async def my_premium(client, message):

    user_id = message.from_user.id

    premium = await check_premium_access(user_id)

    if not premium:

        return await message.reply_text(
            """
❌ No Active Premium Found

Upgrade to premium to access protected files.
"""
        )

    await message.reply_text(
        f"""
👑 Premium Status

✅ Active : Yes

📅 Expiry :
<code>{premium}</code>
"""
    )
    # ================= PREMIUM USERS ================= #

@Bot.on_message(filters.command("premiums") & filters.user(ADMINS))
async def premium_users(client, message):

    users = await get_all_premium_users,
    ban_user,
    unban_user,
    is_banned,
    get_payment_logs,

    if not users:

        return await message.reply_text(
            "❌ No Premium Users Found"
        )

    text = "💎 Premium Users List\n\n"

    count = 1

    for user in users:

        username = user.get("username")

        first_name = user.get("first_name")

        expiry = user.get("premium_expiry")

        if username:
            name = f"@{username}"
        else:
            name = first_name

        text += (
            f"{count}. {name}\n"
            f"⏳ Expiry: {expiry}\n\n"
        )

        count += 1

    text += f"👥 Total Premium Users: {len(users)}"

    await message.reply_text(text[:4000])
    # ================= ADMIN PANEL ================= #


async def build_admin_panel_buttons():

    upi_enabled = await get_upi_enabled()

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("👥 Users", callback_data="admin_users"),
                InlineKeyboardButton("📊 Stats", callback_data="admin_stats")
            ],
            [
                InlineKeyboardButton("💎 Premium Users", callback_data="admin_premium_users"),
                InlineKeyboardButton("💳 Payments", callback_data="admin_payments")
            ],
            [
                InlineKeyboardButton("📈 Sales", callback_data="admin_sales"),
                InlineKeyboardButton("⚠️ Errors", callback_data="admin_errors")
            ],
            [
                InlineKeyboardButton(
                    f"💳 UPI/QR: {'✅ ON' if upi_enabled else '❌ OFF'} (tap to toggle)",
                    callback_data="admin_toggle_upi"
                )
            ],
            [
                InlineKeyboardButton("❌ Close", callback_data="close")
            ]
        ]
    )


@Bot.on_message(filters.command("admin") & filters.private & filters.user(ADMINS))
async def admin_panel(client, message):

    buttons = await build_admin_panel_buttons()

    await message.reply_text(
        "🛠 <b>Admin Panel</b>\n\nChoose an option:",
        reply_markup=buttons
    )
