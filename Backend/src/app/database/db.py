from sqlmodel import create_engine, Session , SQLModel
from src.app.common import get_logger,database_url

logger=get_logger("DataBase")

class PostgreSQL:
    def __init__(self):
        self.url=database_url
        self.client=create_engine(self.url, pool_pre_ping=True)
        logger.info("PostgreSQL Session is established")

    def get_session(self):
        self.session = Session(self.client)
        return self.session
    
    def close_session(self):
        self.session.close()
        logger.info("PostgreSQL session closed")
    
    def create_tables_once(self):
        SQLModel.metadata.create_all(self.client)
        logger.info("Tables created successfully in PostgreSQL")

PostgreSQLDB = PostgreSQL()