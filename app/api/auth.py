from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.user import UserCreate, Token
from app.workflows.auth_workflow import AuthWorkflow
from temporalio.client import Client
from dotenv import load_dotenv
import os

load_dotenv()

router = APIRouter()

@router.post("/register", response_model=Token)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        client = await Client.connect(os.getenv("TEMPORAL_SERVER_URL"))
        result = await client.execute_workflow(
            AuthWorkflow.run,
            args=[db, user],
            id=f"auth-workflow-{user.username}",
            task_queue="workflow-queue"
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=Token)
async def login(user: UserCreate, db: Session = Depends(get_db)):
    try:
        client = await Client.connect(os.getenv("TEMPORAL_SERVER_URL"))
        result = await client.execute_workflow(
            AuthWorkflow.run,
            args=[db, user],
            id=f"auth-workflow-{user.username}",
            task_queue="workflow-queue"
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        ) 