import logging
import os

from pymongo import MongoClient
from pymongo.synchronous.database import Database

logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    pass


def connect_to_db() -> Database:
    mongo_url = os.getenv("MONGO_URL")
    database_name = os.getenv("MONGO_DATABASE", "shortener_db")
    logger.debug("Verifying environment variables")
    if not mongo_url:
        logger.error("MONGO_URL environment variable not set")
        raise DatabaseError("MONGO_URL must be set")

    logger.debug("Connecting to database...")
    try:
        client = MongoClient(
            mongo_url,
            tz_aware=True,
        )
        client.admin.command("ping")
        logger.info("Connected to MongoDB successfully.")
    except Exception as e:
        logger.error(e)
        raise DatabaseError("Could not connect to MongoDB server") from e

    return client[database_name]
