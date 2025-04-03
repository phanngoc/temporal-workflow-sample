from fastapi import FastAPI
from app.api import auth, order, product
from app.db.database import engine
from app.models import user, order as order_model, product as product_model

# Create database tables
user.Base.metadata.create_all(bind=engine)
order_model.Base.metadata.create_all(bind=engine)
product_model.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Temporal API")

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(order.router, prefix="/api/orders", tags=["orders"])
app.include_router(product.router, prefix="/api", tags=["products"])

@app.get("/")
async def root():
    return {"message": "Welcome to Temporal API"} 