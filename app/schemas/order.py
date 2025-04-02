from pydantic import BaseModel, Field
from typing import Optional
from app.models.order import OrderStatus, FailureReason

class OrderBase(BaseModel):
    product_name: str
    quantity: int
    price: float
    shipping_address: str
    
class OrderCreate(OrderBase):
    pass

class OrderResponse(OrderBase):
    id: int
    user_id: int
    total_amount: float
    status: str
    failure_reason: Optional[str] = None
    
    class Config:
        from_attributes = True
        
class OrderUpdate(BaseModel):
    status: Optional[str] = None
    failure_reason: Optional[str] = None 