from base.database import engine,Base,SessionLocal

async def get_db():
    async with engine.begin() as conn:
        # Drop all tables.
        # await conn.run_sync(Base.metadata.drop_all)
        # Create all tables.
        await conn.run_sync(Base.metadata.create_all)  

    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close() 
