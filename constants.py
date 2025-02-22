import os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

MAX_WORKERS = 10
BLACKLISTED_PROXY_PATH = os.path.join(DATA_DIR, "blacklisted_proxies.txt")
WORKING_PROXY_PATH = os.path.join(DATA_DIR, "working_proxies.txt")