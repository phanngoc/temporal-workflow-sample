import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from app.workflows.auth_workflow import AuthWorkflow, register_user, authenticate_user
from app.db.database import SessionLocal
from dotenv import load_dotenv
import os

load_dotenv()

async def main():
    client = await Client.connect(os.getenv("TEMPORAL_SERVER_URL"))
    
    # Create a worker instance
    worker = Worker(
        client,
        task_queue="auth-queue",
        workflows=[AuthWorkflow],
        activities=[register_user, authenticate_user]
    )
    
    # Start the worker
    print("Starting worker...")
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main()) 