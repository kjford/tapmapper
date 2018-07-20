from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from tapmapper import app


Base = declarative_base()


def db_url():
    return "mysql+pymysql://{user}:{pw}@{host}/{db}".format(
        user=app.config["DATABASE_USER"],
        pw=app.config["DATABASE_PASSWORD"],
        host=app.config["DATABASE_HOST"],
        db=app.config["DATABASE_DB"]
    )


engine = create_engine(db_url())


def get_session():
    yield scoped_session(sessionmaker(autocommit=False,
                                      autoflush=False,
                                      bind=engine))


def init_db():
    import tapmapper.models
    Base.metadata.create_all(bind=engine)