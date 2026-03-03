from typing import Optional, Any
from .properties import *


class _Settings:
    _chroma_host:Optional[str] = CHROMA_HOST 
    _chroma_port:Optional[str] = CHROMA_PORT 
    _chroma_face_collection_name=COLLECTION_NAME
    _chroma_construction_parameter=CHROMA_CONSTRUCTION_PARAMETER
    _chroma_search_parameter=CHROMA_SEARCH_PARAMETER
    _db_type=DB_TYPE
    _db_driver=DB_DRIVER
    _db_host:Optional[str] = DB_HOST 
    _db_port:Optional[str] = DB_PORT
    _db_db:Optional[str] = DB_DB
    _db_user:Optional[str] = DB_USER
    _db_password:Optional[str] = DB_PASSWORD
    _redis_host:Optional[str] = REDIS_HOST
    _redis_port:Optional[int] = REDIS_PORT
    _redis_db_camera:Optional[int] = REDIS_DB_CAMERA
    _jwt_secret_key:Optional[str] = SECRET_KEY
    _jwt_algorithm:Optional[str] = ALGORITHM
    _jwt_access_token_expire_minutes:Optional[int] = ACCESS_TOKEN_EXPIRE_MINUTES
    _jwt_refresh_token_expire_days:Optional[int] = REFRESH_TOKEN_EXPIRE_DAYS
    _jwt_blacklist_key:Optional[str] = BLACKLIST_KEY

    def _require(self, value, value_name)->Any:
        if not value:
            raise ValueError(f"Value not set for {value_name}")
        return value
    
    @property
    def chroma_host(self):
        return self._require(self._chroma_host, "CHROMA_HOST")

    @property
    def chroma_port(self):
        return self._require(self._chroma_port, "CHROMA_PORT")

    @property
    def chroma_face_name_collection(self):
        return self._require(self._chroma_face_collection_name, "CHROMA_FACE_COLLECTION_NAME")
    
    @property
    def chroma_construction_parameter(self):
        return self._require(self._chroma_construction_parameter, "CHROMA_CONSTRUCTION_PARAMETER")
    
    @property
    def chroma_search_parameter(self):
        return self._require(self._chroma_search_parameter,"CHROMA_SEARCH_PARAMETER")
    
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
    def redis_host(self):
        return self._require(self._redis_host, "REDIS_HOST")

    @property
    def redis_port(self):
        return self._require(self._redis_port, "REDIS_PORT")
    
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
    def jwt_refresh_token_expire_days(self):
        return self._require(self._jwt_refresh_token_expire_days, "REFRESH_TOKEN_EXPIRE_DAYS")
    
    @property
    def jwt_blacklist_key(self):
        return self._require(self._jwt_blacklist_key, "BLACKLIST_KEY")

Settings =_Settings()
