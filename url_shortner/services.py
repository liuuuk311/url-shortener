from pymongo.synchronous.database import Database
from datetime import datetime, timedelta, timezone
import random
import string
from urllib.parse import urlparse


BASE_SHORT_URL = "https://short.url"


class ServiceError(Exception):
    pass


class InvalidURL(ServiceError):
    pass


class URLNotFound(ServiceError):
    pass


def _is_a_valid_url(url: str) -> bool:
    """
    Check if the given URL is valid.
    A valid URL must have a scheme (http or https) and a network location.
    """
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except (TypeError, ValueError):
        return False


def _generate_short_code(length: int = 6) -> str:
    """
    Generate a random alphanumeric short code of a given length.
    """
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def minify_url(db: Database, url: str, expiration_seconds: int = 3600) -> str:
    """
    Create a shortened URL for the provided complete URL.

    If the URL is already in the database and is not expired, return the existing short URL.
    Otherwise, generate a new short code, store it with the creation time and expiration,
    and return the new shortened URL.
    """
    if not _is_a_valid_url(url):
        raise InvalidURL(f"Invalid URL: {url}")

    urls_collection = db.urls
    now = datetime.now(timezone.utc)

    # Check for an existing non-expired record for this URL.
    record = urls_collection.find_one({"original_url": url, "expires_at": {"$gt": now}})
    if record:
        return f"{BASE_SHORT_URL}/{record['short_code']}"

    # Generate a unique short code.
    short_code = _generate_short_code()
    while urls_collection.find_one({"short_code": short_code}):
        short_code = _generate_short_code()

    expires_at = now + timedelta(seconds=expiration_seconds)
    document = {
        "original_url": url,
        "short_code": short_code,
        "created_at": now,
        "expires_at": expires_at,
    }
    urls_collection.insert_one(document)

    return f"{BASE_SHORT_URL}/{short_code}"


def expand_url(db: Database, url: str) -> str:
    """
    Retrieve the original URL from a shortened URL.

    The function extracts the short code from the provided URL and looks up the corresponding record.
    If no record is found or if the record is expired, it returns an appropriate error message.
    """
    if not _is_a_valid_url(url):
        raise InvalidURL(f"Invalid URL: {url}")

    parsed = urlparse(url)
    short_code = parsed.path.strip("/")  # Extract the short code from the path
    if not short_code:
        raise URLNotFound("No short code found in the URL.")

    urls_collection = db.urls
    record = urls_collection.find_one({"short_code": short_code})
    if not record:
        raise URLNotFound("Shortened URL not found.")

    now = datetime.now(timezone.utc)
    expires_at = record.get("expires_at", now)
    # Convert to timezone-aware datetime (UTC) if not already aware.
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if now > expires_at:
        raise URLNotFound("Shortened URL has expired.")

    return record.get("original_url", "Error: Original URL not found.")
