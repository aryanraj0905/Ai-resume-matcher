import os
from pathlib import Path


DATABASE_PATH = Path(os.getenv("DATABASE_PATH", "resume_matcher.db"))
ENABLE_SEMANTIC_MATCHING = os.getenv("ENABLE_SEMANTIC_MATCHING", "true").lower() == "true"
