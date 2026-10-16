"""Application settings loaded from environment variables."""

import os

# Base URL used to build short links in API responses,
# e.g. "http://localhost:8000/".
BASE_URL: str = os.environ.get("SHORTLY_BASE_URL", "http://localhost:8000/")

# SQLAlchemy database URL. Defaults to a local SQLite file.
DATABASE_URL: str = os.environ.get("SHORTLY_DATABASE_URL", "sqlite:///./shortly.db")

# Length of the generated short code.
SHORT_CODE_LENGTH: int = int(os.environ.get("SHORTLY_CODE_LENGTH", "6"))

# Allowed URL schemes for user-submitted links (security measure).
ALLOWED_SCHEMES: tuple[str, ...] = ("http", "https")
