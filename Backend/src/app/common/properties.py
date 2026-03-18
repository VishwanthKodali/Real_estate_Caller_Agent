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

# JWT Settings
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

#OPENAI Settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ElevenLabs Settings
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_PHONE_NUMBER_ID = os.getenv("ELEVENLABS_PHONE_NUMBER_ID")

# Application Settings
APP_NAME = config.get("APP_NAME", "RealEstate Caller API")

# Upload Settings
UPLOAD_DIR = config.get("UPLOAD_DIR")