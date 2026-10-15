# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Read the environment name (default to 'production' for safety)
ENVIRONMENT = os.getenv("ENVIRONMENT", "production").strip().lower()
GOOGLE_MAPS_URL= os.getenv("GOOGLE_MAPS_URL", None)
print("env:", ENVIRONMENT)
# If production, headless is ALWAYS True; otherwise False for local development
if ENVIRONMENT == "production":
    HEADLESS = True
else:
    HEADLESS = False

browser_args = (
    [
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
    ]
    if HEADLESS
    else []
)    

DESKTOP_CONTEXT_OPTIONS = {
    "viewport": {"width": 1920, "height": 1080},
    "user_agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/130.0.0.0 Safari/537.36"
    ),
    "is_mobile": False,
    "has_touch": False,
    "locale": "en-US",
}    