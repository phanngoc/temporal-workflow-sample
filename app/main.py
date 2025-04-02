from fastapi import FastAPI
from app.api import auth, order
from app.db.database import engine
from app.models import user, order

# Create database tables
user.Base.metadata.create_all(bind=engine)
order.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Temporal API")

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(order.router, prefix="/api/orders", tags=["orders"])

@app.get("/")
async def root():
    return {"message": "Welcome to Temporal API"} 