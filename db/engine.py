from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

url = 'sqlite+aiosqlite:///datab.db'

engine = create_async_engine(
url, 
echo=True
)

AsyncSessionMaker = async_sessionmaker(
    engine,
    expire_on_commit=False
)