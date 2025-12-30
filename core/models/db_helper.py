from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from core.config import setting


class DataBaseHelper:
    def __init__(self, url):
        self.engine = create_async_engine(url=url)
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,)
    async def session(self):
        async with self.session_factory() as sess:
            yield sess

db_helper = DataBaseHelper(url=setting.db_url)