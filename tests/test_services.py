from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest

from services import (
    minify_url,
    expand_url,
    InvalidURL,
    URLNotFound,
)


def test_minify_invalid_url():
    db = MagicMock()
    with pytest.raises(InvalidURL):
        minify_url(db, "not-a-valid-url")


def test_minify_existing_record():
    db = MagicMock()
    # Create a fake record that is not expired.
    fake_record = {
        "original_url": "https://www.example.com",
        "short_code": "ABC123",
        "expires_at": datetime.now(timezone.utc) + timedelta(seconds=100),
    }
    # When querying for the original URL, return the fake record.
    db.urls.find_one.return_value = fake_record

    result = minify_url(db, "https://www.example.com", expiration_seconds=3600)
    expected = f"https://short.url/{fake_record['short_code']}"
    assert result == expected
    # Ensure that no new document was inserted.
    db.urls.insert_one.assert_not_called()


def test_minify_new_record(monkeypatch):
    db = MagicMock()

    # Simulate that no record exists for both queries.
    def fake_find_one(query):
        return None

    db.urls.find_one.side_effect = fake_find_one

    # Patch _generate_short_code to return a fixed value for test predictability.
    monkeypatch.setattr("services._generate_short_code", lambda length=6: "XYZ789")

    result = minify_url(db, "https://www.test.com", expiration_seconds=3600)
    expected = f"https://short.url/XYZ789"
    assert result == expected
    # Check that insert_one was called with a document containing the correct original_url and short_code.
    db.urls.insert_one.assert_called_once()
    inserted_doc = db.urls.insert_one.call_args[0][0]
    assert inserted_doc["original_url"] == "https://www.test.com"
    assert inserted_doc["short_code"] == "XYZ789"


def test_expand_invalid_url():
    db = MagicMock()
    with pytest.raises(InvalidURL):
        expand_url(db, "not-a-valid-url")


def test_expand_no_short_code():
    db = MagicMock()
    # URL with no path content returns an error message.
    with pytest.raises(URLNotFound):
        expand_url(db, f"https://short.url")


def test_expand_record_not_found():
    db = MagicMock()
    # For any query with a short code, return None.
    db.urls.find_one.return_value = None
    with pytest.raises(URLNotFound):
        expand_url(db, f"https://short.url/NONEXIST")


def test_expand_expired_record():
    db = MagicMock()
    # Create a record that is already expired.
    past_time = datetime.now(timezone.utc) - timedelta(seconds=10)
    fake_record = {
        "short_code": "EXP001",
        "expires_at": past_time,
        "original_url": "https://www.expired.com",
    }
    db.urls.find_one.return_value = fake_record
    with pytest.raises(URLNotFound):
        expand_url(db, f"https://short.url/EXP001")


def test_expand_valid_record():
    db = MagicMock()
    future_time = datetime.now(timezone.utc) + timedelta(seconds=1000)
    fake_record = {
        "short_code": "VAL001",
        "expires_at": future_time,
        "original_url": "https://www.valid.com",
    }
    db.urls.find_one.return_value = fake_record
    result = expand_url(db, f"https://short.url/VAL001")
    assert result == fake_record["original_url"]


def test_expand_offset_naive_expires(monkeypatch):
    db = MagicMock()
    # Create a record with an offset-naive expires_at.
    future_time_naive = datetime.now(timezone.utc) + timedelta(
        seconds=1000
    )  # offset-naive datetime
    fake_record = {
        "short_code": "NAIVE1",
        "expires_at": future_time_naive,  # naive timestamp
        "original_url": "https://www.naive.com",
    }
    db.urls.find_one.return_value = fake_record
    # The expand_url function should convert naive datetime to UTC-aware.
    result = expand_url(db, f"https://short.url/NAIVE1")
    assert result == fake_record["original_url"]
