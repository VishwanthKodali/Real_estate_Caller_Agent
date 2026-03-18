import logging
from datetime import datetime
from .settings import Settings
from typing import Optional

logger = logging.getLogger(__name__)

def build_db_url(
    db_type: str,
    driver: Optional[str] = None,
    user: Optional[str] = None,
    password: Optional[str] = None,
    host: Optional[str] = None,
    port: Optional[int] = None,
    database: Optional[str] = None,
) -> str:
    """
    Build a SQLAlchemy database URL.

    Examples:
    - postgresql+psycopg2://user:pass@localhost:5432/db
    - mysql+pymysql://user:pass@localhost:3306/db
    - sqlite:///example.db
    """
    logger.debug(f"build_db_url called db_type={db_type} driver={driver} user={user} host={host} port={port} database={database}")

    # SQLite: special case
    if db_type == "sqlite":
        if database is None:
            raise ValueError("SQLite requires a database file path.")
        result = f"sqlite:///{database}"
        logger.debug(f"build_db_url returning {result}")
        return result

    # base: "postgresql+psycopg2" or "mysql+pymysql"
    if driver:
        dialect = f"{db_type}+{driver}"
    else:
        dialect = db_type

    auth = ""
    if user:
        auth = user
        if password:
            auth += f":{password}"
        auth += "@"

    netloc = ""
    if host:
        netloc = host
        if port:
            netloc += f":{port}"

    if not database:
        raise ValueError("Database name is required for non-SQLite DBs.")

    result = f"{dialect}://{auth}{netloc}/{database}"
    logger.debug(f"build_db_url returning {result}")
    return result

database_url=build_db_url(Settings.db_type,Settings.db_driver,
                          Settings.db_user,Settings.db_password,
                          Settings.db_host,Settings.db_port,
                          Settings.db_db
                          )