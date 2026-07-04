from pymongo import MongoClient
from config import DB_URI, DB_NAME

client = MongoClient(DB_URI)
db = client[DB_NAME]

users = db["users"]
files = db["files"]
failed = db["failed"]

print("Creating indexes...")

# USERS
users.create_index("last_seen")
users.create_index("files_taken")
users.create_index("premium")
users.create_index("premium_expiry")

# FILES
files.create_index("file_id")
files.create_index("downloads")

# FAILED
failed.create_index("user_id")

print("Done!")
