from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = 'sqlite:///./avm.db';

engine = create_engine(DATABASE_URL,connect_args={"check_same_thread":False})
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    pass

@event.listens_for(engine, "connect")
def enable_sqlite_foriengn_keys(dbapi_connection, connection_record):
    if engine.dialect.name == 'sqlite':
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foriegn_keys=ON")
        cursor.close()
    


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()