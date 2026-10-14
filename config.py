# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Read the environment name (default to 'production' for safety)
ENVIRONMENT = os.getenv("ENVIRONMENT", "production").strip().lower()
GOOGLE_MAPS_URL= os.getenv("GOOGLE_MAPS_URL", None)
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
    