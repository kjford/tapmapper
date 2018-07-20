from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from tapmapper import app
from contextlib import contextmanager

Base = declarative_base()


def db_url():
    return "mysql+pymysql://{user}:{pw}@{host}/{db}".format(
        user=app.config["DATABASE_USER"],
        pw=app.config["DATABASE_PASSWORD"],
        host=app.config["DATABASE_HOST"],
        db=app.config["DATABASE_DB"]
    )


engine = create_engine(db_url())
Session = sessionmaker(bind=engine)


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def init_db():
    import tapmapper.models
    Base.metadata.create_all(bind=engine)