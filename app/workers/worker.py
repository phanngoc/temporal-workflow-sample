import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from app.workflows.auth_workflow import AuthWorkflow, register_user, authenticate_user
from app.workflows.order_workflow import OrderWorkflow, validate_order, process_payment, ship_order, send_confirmation
from app.db.database import SessionLocal
from dotenv import load_dotenv
import os

load_dotenv('../.env')
print('TEMPORAL_SERVER_URL', os.getenv("TEMPORAL_SERVER_URL"))

async def main():
    client = await Client.connect(os.getenv("TEMPORAL_SERVER_URL"))
    
    # Create a worker instance
    worker = Worker(
        client,
        task_queue="workflow-queue",
        workflows=[AuthWorkflow, OrderWorkflow],
        activities=[
            # Auth workflow activities
            register_user, 
            authenticate_user,
            # Order workflow activities
            validate_order,
            process_payment,
            ship_order,
            send_confirmation
        ]
    )
    
    # Start the worker
    print("Starting worker...")
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main()) 