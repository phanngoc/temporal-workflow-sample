from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import asyncio

from app.db.database import get_db
from app.models.product import Product, ProductCategory
from app.schemas.product import (
    ProductCreate, 
    ProductUpdate, 
    ProductResponse, 
    ProductStockUpdate,
    LowStockReport
)
from app.workflows.product_workflow import (
    ProductCreateWorkflow,
    ProductStockUpdateWorkflow,
    ProductInventoryCheckWorkflow
)
from app.workers.client import get_client

router = APIRouter(tags=["products"])

@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    client = await get_client()
    
    # Tạo workflow
    result = await client.execute_workflow(
        ProductCreateWorkflow.run,
        product.model_dump(),
        id=f"product-create-{product.name}",
        task_queue="workflow-queue"
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["reason"]
        )
    
    # Lấy sản phẩm từ database
    db_product = db.query(Product).filter(Product.id == result["product_id"]).first()
    return db_product

@router.get("/products", response_model=List[ProductResponse])
def get_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = db.query(Product).offset(skip).limit(limit).all()
    return products

@router.get("/products/low-stock", response_model=LowStockReport)
async def get_low_stock_products(threshold: int = 10):
    client = await get_client()
    
    # Chạy kiểm tra tồn kho thấp
    result = await client.execute_workflow(
        ProductInventoryCheckWorkflow.run,
        threshold,
        id="product-low-stock-check",
        task_queue="workflow-queue"
    )
    
    return {
        "low_stock_count": result["low_stock_count"],
        "products": result["products"]
    }

@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại")
    return product

@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product_update: ProductUpdate, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại")
    
    # Cập nhật các trường được cung cấp
    update_data = product_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product

@router.patch("/products/{product_id}/stock", response_model=ProductResponse)
async def update_product_stock(
    product_id: int, 
    stock_update: ProductStockUpdate, 
    db: Session = Depends(get_db)
):
    client = await get_client()
    
    # Cập nhật tồn kho thông qua workflow
    result = await client.execute_workflow(
        ProductStockUpdateWorkflow.run,
        product_id,
        stock_update.quantity_change,
        id=f"product-stock-update-{product_id}",
        task_queue="workflow-queue"
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["reason"]
        )
    
    # Lấy sản phẩm từ database
    db_product = db.query(Product).filter(Product.id == product_id).first()
    return db_product 