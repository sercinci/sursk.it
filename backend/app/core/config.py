from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[3] / ".env")

APP_NAME = os.getenv("APP_NAME", "Sursk.it")
APP_DOMAIN = os.getenv("APP_DOMAIN", "sursk.it")

# Render automatically injects RENDER=true in all deployed services.
# This detection only works on Render — update if hosting changes.
IS_PROD = os.getenv("RENDER") == "true"

APP_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = APP_DIR.parent
DATA_DIR = APP_DIR / "data"
STATIC_DIR = Path(os.getenv("FRONTEND_DIST", BACKEND_DIR / "static"))

XCORE_CLIENT_ID = os.getenv("XCORE_CLIENT_ID", "")
XCORE_CLIENT_SECRET = os.getenv("XCORE_CLIENT_SECRET", "")
XCORE_REDIRECT_URI = os.getenv("XCORE_REDIRECT_URI", "http://localhost:5173/api/auth/callback")
XCORE_BASE_URL = os.getenv("XCORE_BASE_URL", "https://api.exphub.gg")

SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY", "")
if IS_PROD and not SESSION_SECRET_KEY:
    print("FATAL: SESSION_SECRET_KEY environment variable is not set.", file=sys.stderr)
    sys.exit(1)
