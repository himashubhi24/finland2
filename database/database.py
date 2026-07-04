#(©)CodeXBotz




import pymongo
from datetime import datetime, timedelta
from config import DB_URI, DB_NAME


dbclient = pymongo.MongoClient(DB_URI)

database = dbclient[DB_NAME]


# ================= COLLECTIONS ================= #

user_data = database['users']

files_data = database['files']

failed_data = database['failed']

payments_data = database['payments']

link_stats = database['link_stats']

settings_data = database['settings']

stars_payments_data = database['stars_payments']


# ================= USER SYSTEM ================= #

async def present_user(user_id: int):

    found = user_data.find_one(
        {'_id': user_id}
    )

    return bool(found)


async def add_user(user):

    data = {
        "_id": user.id,
        "first_name": user.first_name,
        "username": user.username,
        "files_taken": 0,
        "last_seen": datetime.utcnow(),
        "joined_date": datetime.utcnow(),

        # PREMIUM SYSTEM
        "premium": False,
        "premium_expiry": None
    }

    user_data.insert_one(data)

    return


async def update_user_activity(user):

    user_data.update_one(
        {"_id": user.id},
        {
            "$set": {
                "first_name": user.first_name,
                "username": user.username,
                "last_seen": datetime.utcnow()
            }
        }
    )


async def increase_files_count(user_id: int):

    user_data.update_one(
        {"_id": user_id},
        {
            "$inc": {
                "files_taken": 1
            }
        }
    )


async def get_top_users(limit=10):

    users = user_data.find().sort(
        "files_taken",
        -1
    ).limit(limit)

    return list(users)


async def get_online_users(minutes=10):

    time_limit = datetime.utcnow() - timedelta(minutes=minutes)

    count = user_data.count_documents(
        {
            "last_seen": {
                "$gte": time_limit
            }
        }
    )

    return count


# ================= PREMIUM SYSTEM ================= #

async def check_premium_access(user_id: int):

    user = user_data.find_one(
        {"_id": user_id}
    )

    if not user:
        return False

    premium = user.get("premium", False)

    if not premium:
        return False

    expiry = user.get("premium_expiry")

    if not expiry:
        return False

    if datetime.utcnow() > expiry:

        user_data.update_one(
            {"_id": user_id},
            {
                "$set": {
                    "premium": False,
                    "premium_expiry": None
                }
            }
        )

        return False

    return expiry


async def give_premium(user_id: int, days: int = 30):

    expiry = datetime.utcnow() + timedelta(days=days)

    user_data.update_one(
        {"_id": user_id},
        {
            "$set": {
                "premium": True,
                "premium_expiry": expiry
            }
        }
    )

    return expiry


async def set_pending_plan(user_id: int, days: int, price: int):
    user_data.update_one(
        {"_id": user_id},
        {
            "$set": {
                "pending_plan_days": days,
                "pending_plan_price": price
            }
        },
        upsert=True
    )


async def get_pending_plan(user_id: int):
    user = user_data.find_one({"_id": user_id})
    if not user:
        return None
    return {
        "days": user.get("pending_plan_days", 30),
        "price": user.get("pending_plan_price", 50)
    }


async def clear_pending_plan(user_id: int):
    user_data.update_one(
        {"_id": user_id},
        {
            "$unset": {
                "pending_plan_days": "",
                "pending_plan_price": ""
            }
        }
    )


async def remove_premium(user_id: int):

    user_data.update_one(
        {"_id": user_id},
        {
            "$set": {
                "premium": False,
                "premium_expiry": None
            }
        }
    )


# ================= FILE SYSTEM ================= #

async def add_file_stats(file_name):

    if not file_name:
        file_name = "Unknown File"

    files_data.update_one(
        {
            "file_name": file_name
        },
        {
            "$inc": {
                "downloads": 1
            }
        },
        upsert=True
    )


async def get_top_files(limit=10):

    files = files_data.find().sort(
        "downloads",
        -1
    ).limit(limit)

    return list(files)


# ================= FAILED LOGS ================= #

async def save_failed_log(user_id, error):

    failed_data.insert_one(
        {
            "user_id": user_id,
            "error": str(error),
            "time": datetime.utcnow()
        }
    )


async def get_failed_logs(limit=20):

    logs = failed_data.find().sort(
        "time",
        -1
    ).limit(limit)

    return list(logs)


# ================= NORMAL FUNCTIONS ================= #

async def full_userbase():

    user_docs = user_data.find()

    user_ids = []

    for doc in user_docs:

        user_ids.append(doc['_id'])

    return user_ids


async def del_user(user_id: int):

    user_data.delete_one(
        {'_id': user_id}
    )

    return 

async def get_premium_users():

    count = user_data.count_documents(
        {
            "premium": True
        }
    )

    return count
    
async def get_all_premium_users():

    users = user_data.find(
        {
            "premium": True
        }
    )

    return list(users)


# ================= LINK ANALYTICS ================= #

async def track_link_view(link_key: str, user_id: int):
    link_stats.update_one(
        {"_id": link_key},
        {
            "$inc": {"views": 1},
            "$addToSet": {"unique_users": user_id},
            "$set": {"last_view": datetime.utcnow()},
            "$setOnInsert": {"created_at": datetime.utcnow(), "downloads": 0}
        },
        upsert=True
    )


async def track_link_download(link_key: str, count: int = 1):
    link_stats.update_one(
        {"_id": link_key},
        {
            "$inc": {"downloads": count},
            "$set": {"last_download": datetime.utcnow()}
        },
        upsert=True
    )


async def get_link_stats(limit: int = 10):
    items = list(link_stats.find().sort("views", -1).limit(limit))
    for item in items:
        item["unique_count"] = len(item.get("unique_users", []))
    return items


# ================= PAYMENT HISTORY ================= #

async def add_payment_log(user_id: int, username: str, plan_days: int, amount: int, status: str):
    payments_data.insert_one(
        {
            "user_id": user_id,
            "username": username,
            "plan_days": plan_days,
            "amount": amount,
            "status": status,
            "date": datetime.utcnow()
        }
    )


async def get_payment_logs(limit: int = 20):
    return list(payments_data.find().sort("date", -1).limit(limit))


# ================= AD UNLOCK SYSTEM ================= #

async def set_ad_unlock(user_id: int, hours: int = 12):
    expiry = datetime.utcnow() + timedelta(hours=hours)

    user_data.update_one(
        {"_id": user_id},
        {
            "$set": {
                "ad_unlock_expiry": expiry
            }
        },
        upsert=True
    )

    return expiry


async def check_ad_unlock(user_id: int):
    user = user_data.find_one({"_id": user_id})

    if not user:
        return False

    expiry = user.get("ad_unlock_expiry")

    if not expiry:
        return False

    if datetime.utcnow() > expiry:
        user_data.update_one(
            {"_id": user_id},
            {"$set": {"ad_unlock_expiry": None}}
        )
        return False

    return expiry


async def get_today_sales():
    start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    logs = list(payments_data.find({"date": {"$gte": start}, "status": "Approved"}))

    report = {
        7: {"count": 0, "amount": 0},
        15: {"count": 0, "amount": 0},
        30: {"count": 0, "amount": 0},
        45: {"count": 0, "amount": 0},
    }

    total = 0

    for item in logs:
        days = int(item.get("plan_days", 0))
        amount = int(item.get("amount", 0))

        if days not in report:
            report[days] = {"count": 0, "amount": 0}

        report[days]["count"] += 1
        report[days]["amount"] += amount
        total += amount

    return report, total


# ================= BAN SYSTEM ================= #

async def ban_user(user_id: int):
    user_data.update_one(
        {"_id": user_id},
        {"$set": {"banned": True}},
        upsert=True
    )


async def unban_user(user_id: int):
    user_data.update_one(
        {"_id": user_id},
        {"$set": {"banned": False}},
        upsert=True
    )


async def is_banned(user_id: int):
    user = user_data.find_one({"_id": user_id})
    if not user:
        return False
    return bool(user.get("banned", False))


# ================= PAYMENT METHOD SETTINGS ================= #

SETTINGS_ID = "payment_settings"


async def get_upi_enabled():
    doc = settings_data.find_one({"_id": SETTINGS_ID})
    if not doc:
        return True
    return bool(doc.get("upi_enabled", True))


async def set_upi_enabled(enabled: bool):
    settings_data.update_one(
        {"_id": SETTINGS_ID},
        {"$set": {"upi_enabled": bool(enabled)}},
        upsert=True
    )
    return enabled


# ================= TELEGRAM STARS PAYMENTS ================= #

async def record_stars_payment(charge_id: str, user_id: int, days: int, amount: int):
    """Atomically records a Stars charge id. Returns True if this is the
    first time it's seen (i.e. safe to grant premium), False if it was
    already processed (duplicate webhook/update delivery)."""

    try:
        stars_payments_data.insert_one(
            {
                "_id": charge_id,
                "user_id": user_id,
                "plan_days": days,
                "amount": amount,
                "date": datetime.utcnow()
            }
        )
        return True

    except pymongo.errors.DuplicateKeyError:
        return False
