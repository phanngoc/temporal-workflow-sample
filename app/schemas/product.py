from pydantic import BaseModel, Field
from typing import Optional, List
from app.models.product import ProductCategory
from datetime import datetime

class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    stock_quantity: int = 0
    category: ProductCategory = ProductCategory.OTHER

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock_quantity: Optional[int] = None
    category: Optional[ProductCategory] = None
    is_active: Optional[bool] = None

class ProductResponse(ProductBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True
    }

class ProductStockUpdate(BaseModel):
    quantity_change: int = Field(..., description="Lượng thay đổi số lượng sản phẩm (+/-)")

class LowStockProduct(BaseModel):
    id: int
    name: str
    current_stock: int

class LowStockReport(BaseModel):
    low_stock_count: int
    products: List[LowStockProduct] 