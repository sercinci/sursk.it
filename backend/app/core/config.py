from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[3] / ".env")

APP_NAME = os.getenv("APP_NAME", "Sursk.it")
APP_DOMAIN = os.getenv("APP_DOMAIN", "sursk.it")
IS_PROD = os.getenv("APP_ENV", "development") == "production"

APP_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = APP_DIR.parent
DATA_DIR = APP_DIR / "data"
STATIC_DIR = Path(os.getenv("FRONTEND_DIST", BACKEND_DIR / "static"))

XCORE_CLIENT_ID = os.getenv("XCORE_CLIENT_ID", "")
XCORE_CLIENT_SECRET = os.getenv("XCORE_CLIENT_SECRET", "")
XCORE_REDIRECT_URI = os.getenv("XCORE_REDIRECT_URI", "http://localhost:5173/api/auth/callback")
XCORE_BASE_URL = os.getenv("XCORE_BASE_URL", "https://api.exphub.gg")

_DEFAULT_SECRET = "dev-insecure-secret-change-in-production"
SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY", _DEFAULT_SECRET)
if IS_PROD and SESSION_SECRET_KEY == _DEFAULT_SECRET:
    print("FATAL: SESSION_SECRET_KEY is not set in production.", file=sys.stderr)
    sys.exit(1)
