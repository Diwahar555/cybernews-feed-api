from __future__ import annotations

import asyncio
import logging
import signal

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import text

from app.core.config import settings
from app.core.logging import configure_logging
from app.db.session import AsyncSessionLocal
from app.ingestion.service import ingest_all
from app.seed import seed

configure_logging()
logger = logging.getLogger(__name__)


async def wait_for_schema() -> None:
    """Wait until the API/migration process has created the application tables."""
    attempt = 0
    while True:
        attempt += 1
        try:
            async with AsyncSessionLocal() as db:
                await db.execute(text("SELECT 1 FROM sources LIMIT 1"))
            return
        except Exception as exc:
            delay = min(30, 2 + attempt * 2)
            logger.warning("database schema not ready; retrying in %ss: %s", delay, exc)
            await asyncio.sleep(delay)


async def run_ingestion() -> None:
    async with AsyncSessionLocal() as db:
        await ingest_all(db)


async def main() -> None:
    await wait_for_schema()
    await seed()
    await run_ingestion()

    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(
        run_ingestion,
        IntervalTrigger(minutes=settings.ingestion_interval_minutes),
        id="cybernews-ingestion",
        max_instances=1,
        coalesce=True,
        misfire_grace_time=300,
    )
    scheduler.start()
    logger.info("worker started interval_minutes=%s", settings.ingestion_interval_minutes)

    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop_event.set)
        except NotImplementedError:
            # Signal handlers are not available on every local development platform.
            pass

    try:
        await stop_event.wait()
    finally:
        scheduler.shutdown(wait=False)
        logger.info("worker stopped")


if __name__ == "__main__":
    asyncio.run(main())
