"""Sweeping logic for cleaning up expired threads and checkpoints."""

import asyncio
from typing import cast

import structlog

from langgraph_api.config import THREAD_TTL
from langgraph_api.feature_flags import FF_USE_CORE_API
from langgraph_runtime.database import connect

logger = structlog.stdlib.get_logger(__name__)

# Supported TTL strategies
SUPPORTED_STRATEGIES = {"delete", "keep_latest"}


async def thread_ttl_sweep_loop():
    """Periodically sweep threads based on TTL configuration.

    Supported strategies:
    - 'delete': Remove the thread and all its data entirely
    - 'keep_latest': Prune old checkpoints but keep thread and latest state
      (requires FF_USE_CORE_API=true)

    Per-thread TTL strategies are stored in the thread_ttl table and can vary
    by thread. This loop processes all expired threads regardless of strategy.
    """
    thread_ttl_config = THREAD_TTL or {}
    default_strategy = thread_ttl_config.get("strategy", "delete")
    sweep_interval_minutes = cast(
        "int", thread_ttl_config.get("sweep_interval_minutes", 5)
    )
    sweep_limit = thread_ttl_config.get("sweep_limit", 1000)

    await logger.ainfo(
        "Starting thread TTL sweeper",
        default_strategy=default_strategy,
        interval_minutes=sweep_interval_minutes,
        sweep_limit=sweep_limit,
        core_api_enabled=FF_USE_CORE_API,
    )

    if default_strategy == "keep_latest" and not FF_USE_CORE_API:
        await logger.awarning(
            "keep_latest strategy configured but FF_USE_CORE_API is not enabled. "
            "Threads with keep_latest strategy will be skipped during sweep."
        )

    loop = asyncio.get_running_loop()

    from langgraph_runtime.ops import Threads

    while True:
        await asyncio.sleep(sweep_interval_minutes * 60)
        try:
            async with connect() as conn:
                sweep_start = loop.time()
                threads_processed, threads_deleted = await Threads.sweep_ttl(conn)
                if threads_processed > 0:
                    await logger.ainfo(
                        "Thread TTL sweep completed",
                        threads_processed=threads_processed,
                        threads_deleted=threads_deleted,
                        duration=loop.time() - sweep_start,
                    )
        except Exception as exc:
            logger.exception("Thread TTL sweep iteration failed", exc_info=exc)
