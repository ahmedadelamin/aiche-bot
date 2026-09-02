import json
import os

USERS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.json")
users = set()
if os.path.exists(USERS_FILE):
    with open(USERS_FILE, "r") as f:
        try:
            users = set(json.load(f))
        except:
            pass

users.add(1846962771)  # Add admin ID by default
with open(USERS_FILE, "w") as f:
    json.dump(list(users), f)
