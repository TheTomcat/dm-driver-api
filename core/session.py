import time
from functools import lru_cache
from typing import Generator

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import scoped_session, sessionmaker

from config import get_settings

# from api.logger import logger


@lru_cache
def get_engine() -> Engine:
    settings = get_settings()
    if settings.PROFILE_QUERIES:

        @event.listens_for(Engine, "before_cursor_execute")
        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            conn.info.setdefault("query_start_time", []).append(time.time())
            # logger.debug(f"Start Query {statement}")

        @event.listens_for(Engine, "after_cursor_execute")
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            total = time.time() - conn.info["query_start_time"].pop(-1)
            # logger.debug("Query Complete!")
            # logger.debug(f"Total time: {total}")

    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
    return engine


@lru_cache
def create_session() -> scoped_session:
    engine = get_engine()
    Session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
    return Session


def get_session() -> Generator[scoped_session, None, None]:
    Session = create_session()
    try:
        yield Session
    finally:
        Session.remove()
