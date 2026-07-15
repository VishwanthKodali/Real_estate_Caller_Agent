from typing import Optional, Any
from .properties import *


class _Settings:
    _db_type=DB_TYPE
    _db_driver=DB_DRIVER
    _db_host:Optional[str] = DB_HOST 
    _db_port:Optional[str] = DB_PORT
    _db_db:Optional[str] = DB_DB
    _db_user:Optional[str] = DB_USER
    _db_password:Optional[str] = DB_PASSWORD
    _jwt_secret_key:Optional[str] = SECRET_KEY
    _jwt_algorithm:Optional[str] = ALGORITHM
    _jwt_access_token_expire_minutes:Optional[int] = ACCESS_TOKEN_EXPIRE_MINUTES
    _openai_api_key:Optional[str] = OPENAI_API_KEY
    _elevenlabs_api_key:Optional[str] = ELEVENLABS_API_KEY
    _elevenlabs_phone_number_id:Optional[str] = ELEVENLABS_PHONE_NUMBER_ID
    _application_name:Optional[str] = APP_NAME
    _upload_dir:Optional[str] = UPLOAD_DIR

    def _require(self, value, value_name)->Any:
        if not value:
            raise ValueError(f"Value not set for {value_name}")
        return value
    
    @property
    def db_type(self):
        return self._require(self._db_type,"DB_TYPE")
    
    @property
    def db_driver(self):
        return self._require(self._db_driver,"DB_DRIVER")
    
    @property
    def db_host(self):
        return self._require(self._db_host, "DB_HOST")

    @property
    def db_port(self):
        return self._require(self._db_port, "DB_PORT")

    @property
    def db_db(self):
        return self._require(self._db_db, "DB_DB")

    @property
    def db_user(self):
        return self._require(self._db_user,"DB_USER")

    @property
    def db_password(self):
        return self._require(self._db_password, "DB_PASSWORD")
    
    @property
    def jwt_secret_key(self):
        return self._require(self._jwt_secret_key, "SECRET_KEY")
    
    @property
    def jwt_algorithm(self):
        return self._require(self._jwt_algorithm, "ALGORITHM")
    
    @property
    def jwt_access_token_expire_minutes(self):
        return self._require(self._jwt_access_token_expire_minutes, "ACCESS_TOKEN_EXPIRE_MINUTES")
    
    @property
    def openai_api_key(self):
        return self._require(self._openai_api_key, "OPENAI_API_KEY")
    
    @property
    def elevenlabs_api_key(self):
        return self._require(self._elevenlabs_api_key, "ELEVENLABS_API_KEY")
    
    @property
    def elevenlabs_phone_number_id(self):
        return self._require(self._elevenlabs_phone_number_id, "ELEVENLABS_PHONE_NUMBER_ID")
    
    @property
    def app_name(self):
        return self._require(self._application_name, "APP_NAME")
    
    @property
    def upload_dir(self):
        return self._require(self._upload_dir, "UPLOAD_DIR")
Settings =_Settings()
