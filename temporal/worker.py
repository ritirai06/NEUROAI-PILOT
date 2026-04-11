"""
Temporal Worker — registers the NeuroAI workflow and all activities.
Run this in a separate terminal: python -m temporal.worker
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from temporalio.client import Client
from temporalio.worker import Worker
from temporal.workflow   import NeuroAIPlanWorkflow, TASK_QUEUE
from temporal.activities import ALL_ACTIVITIES

TEMPORAL_HOST = os.getenv("TEMPORAL_HOST", "localhost:7233")


async def main():
    print(f"[Worker] Connecting to Temporal at {TEMPORAL_HOST}...")
    client = await Client.connect(TEMPORAL_HOST)
    print(f"[Worker] Connected. Task queue: {TASK_QUEUE}")

    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[NeuroAIPlanWorkflow],
        activities=ALL_ACTIVITIES,
    )
    print("[Worker] Running — waiting for tasks...")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
