import os
import asyncio

os.environ["CRBCL_ALLOW_SYNTHETIC_SEEDING"] = "true"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///C:/Users/Shilley Pc/crbcl/backend/synthetic_uat.db"
os.environ["DATABASE_SYNC_URL"] = "sqlite:///C:/Users/Shilley Pc/crbcl/backend/synthetic_uat.db"
os.environ["CRBCL_SYNTHETIC_TEST_PASSWORD"] = "SyntheticUAT2026!SecureKey"
os.environ["SESSION_SECRET"] = "crbcl-synthetic-uat-session-secret-64-character-length-hex-key"

from app.core.config import get_settings
get_settings.cache_clear()

from app.core.database import Base, engine, async_session_factory
from app.core.seed_staging_synthetic import seed_staging_synthetic_data

async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session_factory() as session:
        result = await seed_staging_synthetic_data(session)
        print("SEEDING RESULT:", result)

if __name__ == "__main__":
    asyncio.run(main())
