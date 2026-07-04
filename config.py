#(©)CodeXBotz




import os
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

load_dotenv()


# Bot token @Botfather
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "")

# Your API ID from my.telegram.org
APP_ID = int(os.environ.get("APP_ID", "0"))

# Your API Hash from my.telegram.org
API_HASH = os.environ.get("API_HASH", "")

# Your db channel Id
CHANNEL_ID = int(
    os.environ.get("CHANNEL_ID", "-1002086919404")
)

# OWNER ID
OWNER_ID = int(
    os.environ.get("OWNER_ID", "6810248021")
)

# Port
PORT = os.environ.get("PORT", "8092")

# LOG CHANNEL
LOG_CHANNEL = os.environ.get(
    "LOG_CHANNEL",
    "@finlundlogssss"
)

# Database
DB_URI = os.environ.get("DATABASE_URL", "")

DB_NAME = os.environ.get(
    "DATABASE_NAME",
    "finland2"
)

# Force sub channel id
FORCE_SUB_CHANNEL = int(
    os.environ.get(
        "FORCE_SUB_CHANNEL",
        "-1001429194262"
    )
)

TG_BOT_WORKERS = int(
    os.environ.get("TG_BOT_WORKERS", "32")
)

# Start message
START_MSG = os.environ.get(
    "START_MESSAGE",
    "Hello {first}\n\n you need to join my channel."
)

try:

    ADMINS = [6810248021]

    for x in (os.environ.get("ADMINS", "").split()):

        ADMINS.append(int(x))

except ValueError:

    raise Exception(
        "Your Admins list does not contain valid integers."
    )
UPLOAD_ADMINS = [5353698695]
# Force sub message
FORCE_MSG = os.environ.get(
    "FORCE_SUB_MESSAGE",
    "👋 Hello {first}!\nPlease Join our channel "
)

# Custom Caption
CUSTOM_CAPTION = os.environ.get(
    "@foxylinkk",
)

# Protect content
PROTECT_CONTENT = (
    True
    if os.environ.get(
        'PROTECT_CONTENT',
        "True"
    ) == "True"
    else False
)

# Disable channel button
DISABLE_CHANNEL_BUTTON = (
    os.environ.get(
        "DISABLE_CHANNEL_BUTTON",
        None
    ) == 'False'
)

BOT_STATS_TEXT = "<b>BOT UPTIME</b>\n{uptime}"

USER_REPLY_TEXT = "🚫 !"

ADMINS.append(OWNER_ID)
ADMINS.append(6810248021)

LOG_FILE_NAME = "filesharingbot.txt"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=[
        RotatingFileHandler(
            LOG_FILE_NAME,
            maxBytes=50000000,
            backupCount=10
        ),
        logging.StreamHandler()
    ]
)

logging.getLogger("pyrogram").setLevel(
    logging.WARNING
)

# ================= PREMIUM SYSTEM ================= #

PREMIUM_PRICE = int(
    os.environ.get(
        "PREMIUM_PRICE",
        "15"
    )
)

PREMIUM_DAYS = int(
    os.environ.get(
        "PREMIUM_DAYS",
        "30"
    )
)

PAYMENT_EXPIRY_MINUTES = int(
    os.environ.get(
        "PAYMENT_EXPIRY_MINUTES",
        "15"
    )
)

UPI_ID = os.environ.get(
    "UPI_ID",
    "yourupi@upi"
)

UPI_NAME = os.environ.get(
    "UPI_NAME",
    "Premium Access"
)

QR_IMAGE_PATH = os.environ.get(
    "QR_IMAGE_PATH",
    "qr.png"
)

# ================= PREMIUM PLANS (shared by UPI/QR & Telegram Stars) ================= #
# 1 Star (XTR) = ₹1, so each plan's Stars price equals its rupee price.

PREMIUM_PLANS = [
    {"days": 1, "price": 20},
    {"days": 7, "price": 49},
    {"days": 15, "price": 79},
    {"days": 30, "price": 99},
]


def LOGGER(name: str) -> logging.Logger:

    return logging.getLogger(name)
