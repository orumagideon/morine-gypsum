# app/models/models.py
from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship


# ==========================
# CATEGORY MODEL
# ==========================
class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    description: Optional[str] = None

    # Relationship: one category -> many products
    products: List["Product"] = Relationship(back_populates="category")


# ==========================
# PRODUCT MODEL
# ==========================
class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = None
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")
    price: float
    stock_quantity: int
    image_url: Optional[str] = None

    # Relationships
    category: Optional[Category] = Relationship(back_populates="products")
    order_items: List["OrderItem"] = Relationship(back_populates="product")


# ==========================
# ORDER & ORDER ITEM MODELS
# ==========================
class OrderItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: Optional[int] = Field(default=None, foreign_key="order.id")
    product_id: Optional[int] = Field(default=None, foreign_key="product.id")
    quantity: int = 1
    price: float  # price at time of order

    order: Optional["Order"] = Relationship(back_populates="items")
    product: Optional[Product] = Relationship(back_populates="order_items")


class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    customer_name: str
    customer_phone: str
    delivery_address: str
    status: str = Field(default="Pending")  # Pending, Processing, Shipped, Delivered
    total_price: float
    created_at: datetime = Field(default_factory=datetime.utcnow)

    items: List[OrderItem] = Relationship(back_populates="order")


# ==========================
# ADMIN USER MODEL
# ==========================
class AdminUser(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password_hash: str
