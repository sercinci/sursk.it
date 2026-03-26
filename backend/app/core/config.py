from __future__ import annotations

import os
from pathlib import Path

APP_NAME = os.getenv("APP_NAME", "cater.py")
APP_DOMAIN = os.getenv("APP_DOMAIN", "caterp.ie")

APP_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = APP_DIR.parent
DATA_DIR = APP_DIR / "data"
STATIC_DIR = Path(os.getenv("FRONTEND_DIST", BACKEND_DIR / "static"))
