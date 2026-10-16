"""Business logic: short code generation and URL validation."""

import secrets
from urllib.parse import urlparse

from . import config

# Alphabet sorted so the mapping between number and code is deterministic.
ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def encode_base62(number: int) -> str:
    """Convert a non-negative integer to its base62 representation."""
    if number < 0:
        raise ValueError("number must be non-negative")
    if number == 0:
        return ALPHABET[0]
    digits: list[str] = []
    while number:
        number, rem = divmod(number, len(ALPHABET))
        digits.append(ALPHABET[rem])
    return "".join(reversed(digits))


def generate_short_code(length: int | None = None) -> str:
    """Generate a random, URL-safe short code of the configured length."""
    n = length if length is not None else config.SHORT_CODE_LENGTH
    return "".join(secrets.choice(ALPHABET) for _ in range(n))


def is_allowed_url(url: str) -> bool:
    """Basic validation: the URL must use an allowed scheme and have a host."""
    try:
        parsed = urlparse(url)
    except ValueError:
        return False
    return (
        parsed.scheme in config.ALLOWED_SCHEMES
        and bool(parsed.netloc)
        # No spaces or control characters in the raw URL.
        and url == url.strip()
        and not any(ch in url for ch in "\r\n\t ")
    )
