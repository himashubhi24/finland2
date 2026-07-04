# ================= TELEGRAM STARS (XTR) PAYMENTS ================= #
#
# Pyrogram 2.0.106 has no high-level sendInvoice/pre_checkout_query API,
# so this talks to the raw MTProto layer directly.

import secrets

from pyrogram import raw

from bot import Bot
from config import PREMIUM_PLANS
from database.database import give_premium, add_payment_log, record_stars_payment

STARS_CURRENCY = "XTR"


def get_stars_plan(days: int):
    for plan in PREMIUM_PLANS:
        if plan["days"] == days:
            return plan
    return None


async def send_stars_invoice(client: Bot, chat_id: int, days: int, price: int):
    title = f"Premium Access - {days} Days"
    description = f"Unlock protected files for {days} days."
    payload = f"stars_{chat_id}_{days}_{price}_{secrets.token_hex(8)}".encode()

    invoice = raw.types.Invoice(
        currency=STARS_CURRENCY,
        prices=[raw.types.LabeledPrice(label=title, amount=price)]
    )

    media = raw.types.InputMediaInvoice(
        title=title,
        description=description,
        invoice=invoice,
        payload=payload,
        provider="",
        provider_data=raw.types.DataJSON(data="{}")
    )

    peer = await client.resolve_peer(chat_id)

    await client.invoke(
        raw.functions.messages.SendMedia(
            peer=peer,
            media=media,
            message="",
            random_id=client.rnd_id()
        )
    )


@Bot.on_raw_update()
async def stars_raw_update_handler(client: Bot, update, users, chats):

    # ================= PRE CHECKOUT ================= #

    if isinstance(update, raw.types.UpdateBotPrecheckoutQuery):

        try:
            await client.invoke(
                raw.functions.messages.SetBotPrecheckoutResults(
                    query_id=update.query_id,
                    success=True
                )
            )
        except Exception as e:
            client.LOGGER(__name__).warning(f"Precheckout answer failed: {e}")

        return

    # ================= SUCCESSFUL PAYMENT ================= #

    if isinstance(update, raw.types.UpdateNewMessage):

        message = update.message

        action = getattr(message, "action", None)

        if isinstance(action, raw.types.MessageActionPaymentSentMe):

            user_id = None
            peer_id = getattr(message, "peer_id", None)

            if isinstance(peer_id, raw.types.PeerUser):
                user_id = peer_id.user_id

            payload = action.payload.decode(errors="ignore") if action.payload else ""

            days = None
            price = int(action.total_amount)

            parts = payload.split("_")
            if len(parts) >= 4 and parts[0] == "stars":
                try:
                    if user_id is None:
                        user_id = int(parts[1])
                    days = int(parts[2])
                except ValueError:
                    pass

            if user_id is None or days is None:
                client.LOGGER(__name__).warning(
                    f"Could not parse Stars payment payload: {payload}"
                )
                return

            charge_id = action.charge.id

            is_new = await record_stars_payment(charge_id, user_id, days, price)

            if not is_new:
                return

            await give_premium(user_id, days)

            await add_payment_log(
                user_id,
                "",
                days,
                price,
                "Approved (Stars)"
            )

            try:
                await client.send_message(
                    chat_id=user_id,
                    text=f"""
🎉 Payment Verified Successfully

✅ Premium Activated via ⭐ Telegram Stars
📅 Validity: {days} Days

Now you can access all protected files.
"""
                )
            except Exception as e:
                client.LOGGER(__name__).warning(f"Stars grant notify failed: {e}")
