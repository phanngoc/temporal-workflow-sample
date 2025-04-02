from datetime import timedelta
from temporalio import workflow, activity
from app.core.security import get_password_hash, verify_password, create_access_token
from app.schemas.user import UserCreate, Token
from app.models.user import User
from sqlalchemy.orm import Session

@activity.defn
async def register_user(db: Session, user: UserCreate) -> User:
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=get_password_hash(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@activity.defn
async def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

@workflow.defn
class AuthWorkflow:
    @workflow.run
    async def run(self, db: Session, user_data: UserCreate) -> Token:
        # Register user
        user = await workflow.execute_activity(
            register_user,
            args=[db, user_data],
            start_to_close_timeout=timedelta(seconds=10)
        )
        
        # Authenticate user
        authenticated_user = await workflow.execute_activity(
            authenticate_user,
            args=[db, user_data.username, user_data.password],
            start_to_close_timeout=timedelta(seconds=10)
        )
        
        if not authenticated_user:
            raise ValueError("Authentication failed")
            
        # Create access token
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": authenticated_user.username},
            expires_delta=access_token_expires
        )
        
        return Token(access_token=access_token, token_type="bearer") 