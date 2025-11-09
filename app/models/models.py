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
    parent_id: Optional[int] = Field(default=None, foreign_key="category.id")

    # Relationship: one category -> many products
    products: List["Product"] = Relationship(back_populates="category")
    parent: Optional["Category"] = Relationship(back_populates="children", sa_relationship_kwargs={"remote_side": "Category.id"})
    children: List["Category"] = Relationship(back_populates="parent")


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
# CUSTOMER MODEL
# ==========================
class Customer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: Optional[str] = Field(default=None, unique=True)
    phone: Optional[str] = Field(default=None, unique=True)
    address: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # The database schema for orders in this project does not include a customer_id
    # foreign key on the Order table (orders are stored with customer_name/email/phone).
    # To avoid SQLAlchemy NoForeignKeysError we DO NOT define a relationship here
    # that relies on a missing foreign key. Invoice still has a customer_id FK so
    # we keep that relationship.
    invoices: List["Invoice"] = Relationship(back_populates="customer")


# ==========================
# SUPPLIER MODEL
# ==========================
class Supplier(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None

    products: List["ProductSupply"] = Relationship(back_populates="supplier")


# ==========================
# PRODUCT SUPPLY MODEL (Supplier-Product Link)
# ==========================
class ProductSupply(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    supplier_id: Optional[int] = Field(default=None, foreign_key="supplier.id")
    product_id: Optional[int] = Field(default=None, foreign_key="product.id")
    supply_date: datetime = Field(default_factory=datetime.utcnow)
    quantity_supplied: int
    cost_price: float

    supplier: Optional[Supplier] = Relationship(back_populates="products")
    product: Optional[Product] = Relationship()


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
    # customer_id removed - not in existing database schema
    # customer_id: Optional[int] = Field(default=None, foreign_key="customer.id")
    customer_name: str
    customer_email: Optional[str] = None
    customer_phone: str
    delivery_address: str
    status: str = Field(default="pending")  # pending, processing, shipped, completed, cancelled
    payment_method: Optional[str] = None  # mpesa, cash_on_delivery, bank_transfer
    payment_status: str = Field(default="pending")  # pending, verified, paid, failed
    mpesa_code: Optional[str] = None  # MPESA confirmation code
    payment_verified: bool = Field(default=False)
    total_amount: Optional[float] = None  # Total including shipping
    total_price: float  # Subtotal
    shipping_cost: float = Field(default=500.0)
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # customer: Optional[Customer] = Relationship(back_populates="orders")  # Commented out since customer_id removed
    items: List[OrderItem] = Relationship(back_populates="order")
    invoices: List["Invoice"] = Relationship(back_populates="order")


# ==========================
# INVOICE MODEL
# ==========================
class Invoice(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: Optional[int] = Field(default=None, foreign_key="order.id")
    customer_id: Optional[int] = Field(default=None, foreign_key="customer.id")
    invoice_date: datetime = Field(default_factory=datetime.utcnow)
    total_amount: float
    payment_status: str = Field(default="Unpaid")  # Unpaid, Paid, Pending
    payment_method: Optional[str] = None
    remarks: Optional[str] = None

    order: Optional[Order] = Relationship(back_populates="invoices")
    customer: Optional[Customer] = Relationship(back_populates="invoices")


# ==========================
# ADMIN USER MODEL
# ==========================
class AdminUser(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    # New email field (nullable) to allow login by email while keeping `username`
    # for backward compatibility. We add this in a non-destructive way so existing
    # databases without the column continue to work; an idempotent ALTER is handled
    # in `app/db/init_db.py`.
    email: Optional[str] = Field(default=None, index=True, unique=True)
    password_hash: str
