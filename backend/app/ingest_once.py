from __future__ import annotations

import asyncio

from app.db.session import AsyncSessionLocal
from app.ingestion.service import ingest_all
from app.seed import seed


async def main() -> None:
    await seed()
    async with AsyncSessionLocal() as db:
        results = await ingest_all(db)
    for result in results:
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
