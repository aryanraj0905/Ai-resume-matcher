import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DATABASE_PATH = Path(os.getenv("DATABASE_PATH", "resume_matcher.db"))
ENABLE_SEMANTIC_MATCHING = os.getenv("ENABLE_SEMANTIC_MATCHING", "true").lower() == "true"

# Comma-separated list of origins allowed to call this API (e.g. your Vercel
# frontend URL). Defaults to common local dev ports for Vite.
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]
