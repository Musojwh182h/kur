import asyncio
from db.engine import engine as eng
from db.models import Base

async def init_models():
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

asyncio.run(init_models())
