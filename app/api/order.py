from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.schemas.order import OrderCreate, OrderResponse, OrderUpdate
from app.models.order import Order, OrderStatus
from app.workflows.order_workflow import OrderWorkflow
from temporalio.client import Client
from dotenv import load_dotenv
import os
from uuid import uuid4

load_dotenv()

router = APIRouter()

@router.post("", response_model=OrderResponse)
async def create_order(order: OrderCreate, db: Session = Depends(get_db), user_id: int = 1):
    """
    Tạo đơn hàng mới và bắt đầu workflow xử lý đơn hàng
    """
    # Tạo đơn hàng mới trong database
    db_order = Order(
        user_id=user_id,
        product_name=order.product_name,
        quantity=order.quantity,
        price=order.price,
        total_amount=order.quantity * order.price,
        shipping_address=order.shipping_address,
        status=OrderStatus.RECEIVED
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # Bắt đầu workflow xử lý đơn hàng
    try:
        client = await Client.connect(os.getenv("TEMPORAL_SERVER_URL"))
        # Ghi chú: Workflow được thực thi không đồng bộ
        await client.start_workflow(
            OrderWorkflow.run,
            args=[db_order.id],
            id=f"order-workflow-{db_order.id}-{uuid4()}",
            task_queue="workflow-queue"
        )
        return OrderResponse.model_validate(db_order)
    except Exception as e:
        # Trong trường hợp lỗi, đánh dấu đơn hàng thất bại
        db_order.status = OrderStatus.FAILED
        db.commit()
        db.refresh(db_order)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start order workflow: {str(e)}"
        )

@router.get("", response_model=List[OrderResponse])
async def get_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Lấy danh sách đơn hàng
    """
    orders = db.query(Order).offset(skip).limit(limit).all()
    return orders

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, db: Session = Depends(get_db)):
    """
    Lấy thông tin chi tiết của một đơn hàng
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return order 