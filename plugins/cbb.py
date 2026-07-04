#(©)Codexbotz

from pyrogram import __version__, enums
import asyncio

from bot import Bot

from config import (
    OWNER_ID,
    ADMINS,
    PREMIUM_PRICE,
    PREMIUM_DAYS,
    UPI_ID,
    PREMIUM_PLANS
)

from database.database import give_premium, set_pending_plan, clear_pending_plan, remove_premium, get_pending_plan, add_payment_log, full_userbase, get_online_users, get_premium_users, get_failed_logs, get_all_premium_users, get_payment_logs, get_today_sales, get_upi_enabled, set_upi_enabled

from plugins.stars import send_stars_invoice

import asyncio

from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)


async def delete_later(msg, sec=30):
    await asyncio.sleep(sec)
    try:
        await msg.delete()
    except:
        pass


@Bot.on_callback_query()

async def cb_handler(client: Bot, query: CallbackQuery):

    data = query.data

    # ================= ABOUT ================= #

    if data == "about":

        await query.message.edit_text(
            text=(
                f"<b>"
                f"○ Creator : <a href='tg://user?id={OWNER_ID}'>This Person</a>\n"
                f"○ Language : <code>Python3</code>\n"
                f"○ Library : <a href='https://docs.pyrogram.org/'>Pyrogram asyncio {__version__}</a>\n"
                f"○ Premium Protected File Sharing Bot\n"
                f"</b>"
            ),

            disable_web_page_preview=True,

            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "🔒 Close",
                            callback_data="close"
                        )
                    ]
                ]
            )
        )

        # ================= BUY ACCESS ================= #

    elif data == "buy_access":

        upi_enabled = await get_upi_enabled()

        rows = []

        if upi_enabled:
            rows.append([
                InlineKeyboardButton("💳 Pay via UPI/QR", callback_data="pay_method_upi")
            ])

        rows.append([
            InlineKeyboardButton("⭐ Pay via Telegram Stars", callback_data="pay_method_stars")
        ])

        rows.append([
            InlineKeyboardButton("🔒 Close", callback_data="close")
        ])

        buttons = InlineKeyboardMarkup(rows)

        await query.message.delete()

        note = "" if upi_enabled else "\n⚠️ UPI/QR is temporarily unavailable. Please use Telegram Stars.\n"

        plan_msg = await client.send_message(
            chat_id=query.from_user.id,
            text=f"""
💎 Get Premium Access

Choose a payment method 👇
{note}""",
            reply_markup=buttons
        )
        asyncio.create_task(delete_later(plan_msg, 30))

    elif data == "pay_method_upi":

        if not await get_upi_enabled():
            return await query.answer(
                "UPI/QR payments are currently disabled by the admin.",
                show_alert=True
            )

        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        f"{p['days']} Day{'s' if p['days'] != 1 else ''} ₹{p['price']}",
                        callback_data=f"plan_{p['days']}_{p['price']}"
                    )
                    for p in PREMIUM_PLANS[i:i + 2]
                ]
                for i in range(0, len(PREMIUM_PLANS), 2)
            ] + [
                [
                    InlineKeyboardButton("🔙 Back", callback_data="buy_access"),
                    InlineKeyboardButton("🔒 Close", callback_data="close")
                ]
            ]
        )

        await query.message.edit_text(
            "💳 Pay via UPI/QR\n\nSelect a plan below 👇",
            reply_markup=buttons
        )

    elif data == "pay_method_stars":

        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        f"{p['days']} Day{'s' if p['days'] != 1 else ''} ⭐{p['price']}",
                        callback_data=f"starsplan_{p['days']}_{p['price']}"
                    )
                    for p in PREMIUM_PLANS[i:i + 2]
                ]
                for i in range(0, len(PREMIUM_PLANS), 2)
            ] + [
                [
                    InlineKeyboardButton("🔙 Back", callback_data="buy_access"),
                    InlineKeyboardButton("🔒 Close", callback_data="close")
                ]
            ]
        )

        await query.message.edit_text(
            "⭐ Pay via Telegram Stars\n\nSelect a plan below 👇",
            reply_markup=buttons
        )

    elif data.startswith("starsplan_"):

        parts = data.split("_")
        days = int(parts[1])
        price = int(parts[2])

        await query.answer()

        try:
            await send_stars_invoice(client, query.from_user.id, days, price)
        except Exception as e:
            client.LOGGER(__name__).warning(f"Stars invoice send failed: {e}")
            await client.send_message(
                chat_id=query.from_user.id,
                text="⚠️ Could not create the Stars invoice. Please try again later."
            )

    elif data == "admin_toggle_upi":

        if query.from_user.id not in ADMINS:
            return await query.answer("Not authorized.", show_alert=True)

        new_state = not await get_upi_enabled()
        await set_upi_enabled(new_state)

        await query.answer(
            f"UPI/QR payments turned {'ON' if new_state else 'OFF'}",
            show_alert=True
        )

        from plugins.start import build_admin_panel_buttons

        await query.message.edit_reply_markup(
            reply_markup=await build_admin_panel_buttons()
        )

    elif data.startswith("plan_"):

        if not await get_upi_enabled():
            return await query.answer(
                "UPI/QR payments are currently disabled by the admin.",
                show_alert=True
            )

        parts = data.split("_")
        days = parts[1]
        price = parts[2]

        await set_pending_plan(query.from_user.id, int(days), int(price))

        payment_text = f"""
💎 Premium Plan

📅 Validity: {days} Days
💰 Price: ₹{price}

Scan QR and complete payment.
After payment, click ✅ I Paid.
"""

        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "✅ I Paid",
                        callback_data=f"i_paid_{days}_{price}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🔙 Back",
                        callback_data="buy_access"
                    ),
                    InlineKeyboardButton(
                        "🔒 Close",
                        callback_data="close"
                    )
                ]
            ]
        )

        qr_msg = await query.message.reply_photo(
            photo=f"qr_{days}.png",
            caption=payment_text,
            reply_markup=buttons
        )

        await query.message.delete()


        await asyncio.sleep(30)

        try:
            await qr_msg.delete()
        except:
            pass

        # ================= PAYMENT SCREENSHOT ================= #

    elif data.startswith("i_paid"):

        await query.message.delete()

        paid_msg = await client.send_message(
            chat_id=query.from_user.id,
            text="""
⚠️ Fake payment = no response

✅ Amount visible
✅ UPI visible
✅ Time visible
✅ Payment successful visible

📤 Upload Payment Screenshot below
"""
        )
        asyncio.create_task(delete_later(paid_msg, 30))
        # ================= ADMIN USERS ================= #

    elif data == "admin_users":

        from database.database import full_userbase

        users = await full_userbase()

        await query.message.edit_text(
            f"👥 Total Users: {len(users)}"
        )


# ================= ADMIN STATS ================= #

    elif data == "admin_stats":

        from database.database import get_online_users, get_premium_users, full_userbase

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
"""

        await query.message.edit_text(text)



    elif data == "admin_premium_users":

        from database.database import get_all_premium_users

        users = await get_all_premium_users()

        if not users:
            return await query.message.edit_text("💎 No premium users found.")

        text = "💎 Premium Users\n\n"

        for user in users[:20]:
            uid = user.get("_id")
            name = user.get("first_name", "Unknown")
            username = user.get("username")
            expiry = user.get("premium_expiry")

            uname = f"@{username}" if username else "No username"
            expiry_text = expiry.strftime("%d %b %Y") if expiry else "N/A"

            text += f"👤 {name} ({uname})\n🆔 <code>{uid}</code>\n⏳ {expiry_text}\n\n"

        await query.message.edit_text(text)

    elif data == "admin_payments":

        from database.database import get_payment_logs

        logs = await get_payment_logs(10)

        if not logs:
            return await query.message.edit_text("💳 No payment history found.")

        text = "💳 Payment History\n\n"

        for item in logs:
            date = item.get("date")
            date_text = date.strftime("%d %b %Y %H:%M") if date else "N/A"

            text += (
                f"👤 User ID: <code>{item.get('user_id')}</code>\n"
                f"📅 Plan: {item.get('plan_days')} Days\n"
                f"💰 Amount: ₹{item.get('amount')}\n"
                f"📌 Status: {item.get('status')}\n"
                f"🕒 {date_text}\n\n"
            )

        await query.message.edit_text(text)

    elif data == "admin_sales":

        from database.database import get_today_sales

        report, total = await get_today_sales()

        text = "📈 Today Sales\n\n"

        for days in [1, 7, 15, 30]:
            item = report.get(days, {"count": 0, "amount": 0})
            text += f"{days} Days : {item['count']} sales — ₹{item['amount']}\n"

        text += f"\n💰 Total Revenue: ₹{total}"

        await query.message.edit_text(text)

    elif data == "admin_errors":

        from database.database import get_failed_logs

        logs = await get_failed_logs()

        if not logs:
            return await query.message.edit_text("✅ No failed logs found.")

        text = "⚠️ Recent Errors\n\n"

        for log in logs[:10]:
            text += f"👤 {log.get('user_id')}\n❌ {log.get('error')}\n\n"

        await query.message.edit_text(text[:4000])


    elif data.startswith("manual_add_"):

        parts = data.split("_")
        user_id = int(parts[2])
        days = int(parts[3])

        await give_premium(user_id, days)

        await client.send_message(
            chat_id=user_id,
            text=f"""
🎉 Premium Activated

✅ Validity: {days} Days
"""
        )

        await query.answer(f"Added {days} days", show_alert=True)

    elif data.startswith("manual_remove_"):

        user_id = int(data.split("_")[2])

        await remove_premium(user_id)

        await client.send_message(
            chat_id=user_id,
            text="❌ Your premium has been removed."
        )

        await query.answer("Premium removed", show_alert=True)


    # ================= APPROVE PAYMENT ================= #

    elif data.startswith("approve_"):

        parts = data.split("_")
        user_id = int(parts[1])
        days = int(parts[2]) if len(parts) > 2 else PREMIUM_DAYS

        await give_premium(
            user_id,
            days
        )

        plan = await get_pending_plan(user_id)
        amount = int(plan.get("price", 0)) if plan else 0

        await add_payment_log(
            user_id,
            "",
            days,
            amount,
            "Approved"
        )

        await clear_pending_plan(user_id)

        await client.send_message(
            chat_id=user_id,
            text=f"""
🎉 Payment Verified Successfully

✅ Premium Activated
📅 Validity: {days} Days

Now you can access all protected files.
"""
        )

        await query.message.edit_caption(
            caption=(
                query.message.caption +
                "\n\n✅ PAYMENT APPROVED"
            )
        )

        await query.answer(
            "Premium Activated"
        )

    # ================= REJECT PAYMENT ================= #

    elif data.startswith("reject_"):

        user_id = int(
            data.split("_")[1]
        )

        try:

            plan = await get_pending_plan(user_id)
            reject_days = int(plan.get("days", 0)) if plan else 0
            reject_amount = int(plan.get("price", 0)) if plan else 0

            await add_payment_log(
                user_id,
                "",
                reject_days,
                reject_amount,
                "Rejected"
            )

            await remove_premium(user_id)

            await client.send_message(
                chat_id=user_id,
                text="""
❌ Payment Verification Failed

Your screenshot could not be verified.

Please send a valid payment screenshot.
"""
            )

        except:
            pass

        await query.message.edit_caption(
            caption=(
                query.message.caption +
                "\n\n❌ PAYMENT REJECTED"
            )
        )

        await query.answer(
            "Payment Rejected"
        )

    # ================= CLOSE ================= #

    elif data == "close":

        await query.message.delete()

        try:

            await query.message.reply_to_message.delete()

        except:

            pass
