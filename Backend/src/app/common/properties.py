import os
import yaml

# Path to config.yml (adjust if needed)
CONFIG_PATH = os.getenv("CONFIG_PATH", "config.yml")

# Load YAML configuration
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

#PostgreSQL setting
DB_TYPE= config.get("DB_TYPE")
DB_DRIVER=config.get("DB_DRIVER")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_DB = os.getenv("DB_DB")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


# Redis Settings
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_DB_CAMERA = os.getenv("REDIS_DB_CAMERA")

# -----------------------------
# ChromaDB Settings
# -----------------------------
CHROMA_HOST = os.getenv("CHROMA_HOST")
CHROMA_PORT = os.getenv("CHROMA_PORT")
COLLECTION_NAME = config.get("COLLECTION_NAME")
CHROMA_CONSTRUCTION_PARAMETER = config.get("CHROMA_CONSTRUCTION_PARAMETER")
CHROMA_SEARCH_PARAMETER = config.get("CHROMA_SEARCH_PARAMETER")

# JWT Settings
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))
BLACKLIST_KEY = os.getenv("BLACKLIST_KEY")