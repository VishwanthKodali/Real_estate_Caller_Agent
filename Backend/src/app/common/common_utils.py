import redis.asyncio as aioredis  # type: ignore
import chromadb
from datetime import datetime
import pytz
from .settings import Settings
from typing import Optional

def async_redis_client():
    """Return an async Redis client compatible with `await client.keys(...)`.

    Uses `redis.asyncio` when available. If it's not available, raises ImportError
    so callers can fall back to a sync client or an executor-based approach.
    """
    if aioredis is None:
        raise ImportError("async redis client (redis.asyncio) is not available in this environment")
    return aioredis.Redis(host=Settings.redis_host, port=Settings.redis_port, db=Settings.redis_db_camera)

def chroma_client():
    chroma_client_object = chromadb.HttpClient(host=Settings.chroma_host, port=Settings.chroma_port)
    return chroma_client_object

def chroma_collection():
    """Chroma collection will be returned"""
    chroma_client_object=chroma_client()
    chroma_collection = chroma_client_object.get_or_create_collection(
            name=Settings.chroma_face_name_collection,
            configuration={
                "hnsw": {
                        "space": "cosine",
                        "ef_construction": Settings.chroma_construction_parameter,
                        "ef_search":Settings.chroma_search_parameter
                        }
            }
            )
    return chroma_collection

def date_time():
    time_str = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%H:%M")
    date_str = datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d")
    
    return time_str,date_str

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

    # SQLite: special case
    if db_type == "sqlite":
        if database is None:
            raise ValueError("SQLite requires a database file path.")
        return f"sqlite:///{database}"

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

    return f"{dialect}://{auth}{netloc}/{database}"

database_url=build_db_url(Settings.db_type,Settings.db_driver,
                          Settings.db_user,Settings.db_password,
                          Settings.db_host,Settings.db_port,
                          Settings.db_db
                          )