# mongodb.py

from pymongo import MongoClient

# Підключення до локального MongoDB (localhost:27017)
client = MongoClient("mongodb://localhost:27017/")

# Назва бази: dragoncollect
mongo_db = client["dragoncollect"]

# Колекція для збереження повідомлень з support.html
support_collection = mongo_db["support_messages"]
