import os
from dotenv import load_dotenv

load_dotenv()

TRACKER_API = os.getenv("TRACKER_API")
TRACKER_USERNAME = os.getenv("TRACKER_USERNAME")
TRACKER_PASSWORD = os.getenv("TRACKER_PASSWORD")
DEFAULT_PAGE_SIZE = int(os.getenv("DEFAULT_PAGE_SIZE", "100"))

if not TRACKER_API:
    raise RuntimeError("Missing TRACKER_API in .env")

if not TRACKER_USERNAME:
    raise RuntimeError("Missing TRACKER_USERNAME in .env")

if not TRACKER_PASSWORD:
    raise RuntimeError("Missing TRACKER_PASSWORD in .env")