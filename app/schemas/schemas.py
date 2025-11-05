# app/schemas/schemas.py
from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel


# ============================================
# CATEGORY SCHEMAS
# ============================================
class CategoryBase(SQLModel):
    name: str
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryRead(CategoryBase):
    id: int

    class Config:
        orm_mode = True


class CategoryUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None


# ==========================
# PRODUCT SCHEMAS
# ==========================
class ProductBase(SQLModel):
    name: str
    description: Optional[str] = None
    price: float
    stock_quantity: int
    image_url: Optional[str] = None
    category_id: Optional[int] = None


class ProductCreate(ProductBase):
    pass


class ProductRead(ProductBase):
    id: int

    class Config:
        orm_mode = True

class ProductUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock_quantity: Optional[int] = None
    image_url: Optional[str] = None
    category_id: Optional[int] = None


# ==========================
# ORDER ITEM SCHEMAS
# ==========================
class OrderItemBase(SQLModel):
    product_id: int
    quantity: int
    price: float


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemRead(OrderItemBase):
    id: int


# ==========================
# ORDER SCHEMAS
# ==========================
class OrderBase(SQLModel):
    customer_name: str
    customer_phone: str
    delivery_address: str


class OrderCreate(OrderBase):
    items: List[OrderItemCreate]


class OrderRead(OrderBase):
    id: int
    status: str
    total_price: float
    created_at: datetime
    items: List[OrderItemRead]


# ==========================
# ADMIN USER SCHEMAS
# ==========================
class AdminUserBase(SQLModel):
    username: str


class AdminUserCreate(AdminUserBase):
    password: str


class AdminUserRead(AdminUserBase):
    id: int
