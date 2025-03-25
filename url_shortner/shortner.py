import argparse
import logging
import sys

from pymongo.synchronous.database import Database

from database import connect_to_db, DatabaseError
from services import minify_url, expand_url, ServiceError

logger = logging.getLogger(__name__)


def _setup_arg_parser():
    parser = argparse.ArgumentParser(
        description="A simple URL Shortener tool",
        epilog="Ensure the MONGO_URL environment variable is set (e.g., 'export MONGO_URL=mongodb://mongo:27017/shortener_db').",
    )
    minify_or_expand_group = parser.add_mutually_exclusive_group(required=True)
    minify_or_expand_group.add_argument(
        "--minify", help="Minify a complete URL", metavar="URL"
    )
    minify_or_expand_group.add_argument(
        "--expand", help="Expand a shortened URL", metavar="URL"
    )
    parser.add_argument(
        "--expiration",
        type=int,
        default=3600,
        help="Expiration time in seconds for the shortened URL (default: 3600 seconds)",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)",
    )
    return parser.parse_args()


def _setup_logger(log_level):
    logger.setLevel(logging.getLevelName(log_level))
    logger.addHandler(logging.StreamHandler(sys.stdout))


def main():
    args = _setup_arg_parser()
    _setup_logger(args.log_level)

    try:
        db: Database = connect_to_db()
    except DatabaseError as e:
        logger.error(
            "Could not connect to database. Have you set `MONGO_URL` in your environment?"
        )
        return sys.exit(1)

    try:
        out = (
            minify_url(db, args.minify, args.expiration)
            if args.minify
            else expand_url(db, args.expand)
        )
    except ServiceError as e:
        logger.error(e)
    else:
        logger.info(out)


if __name__ == "__main__":
    main()
