from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel


# ============================================
# CATEGORY SCHEMAS
# ============================================
class CategoryBase(SQLModel):
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryRead(CategoryBase):
    id: int
    parent_id: Optional[int] = None

    class Config:
        orm_mode = True


class CategoryUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None


# ============================================
# PRODUCT SCHEMAS
# ============================================
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
    category: Optional["CategoryRead"] = None

    class Config:
        orm_mode = True


class ProductUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock_quantity: Optional[int] = None
    image_url: Optional[str] = None
    category_id: Optional[int] = None


# ============================================
# CUSTOMER SCHEMAS
# ============================================
class CustomerBase(SQLModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerRead(CustomerBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class CustomerUpdate(SQLModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


# ============================================
# SUPPLIER SCHEMAS
# ============================================
class SupplierBase(SQLModel):
    name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None


class SupplierCreate(SupplierBase):
    pass


class SupplierRead(SupplierBase):
    id: int

    class Config:
        orm_mode = True


class SupplierUpdate(SQLModel):
    name: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None


# ============================================
# PRODUCT SUPPLY SCHEMAS
# ============================================
class ProductSupplyBase(SQLModel):
    supplier_id: int
    product_id: int
    quantity_supplied: int
    cost_price: float


class ProductSupplyCreate(ProductSupplyBase):
    pass


class ProductSupplyRead(ProductSupplyBase):
    id: int
    supply_date: datetime

    class Config:
        orm_mode = True


# ============================================
# ORDER ITEM SCHEMAS
# ============================================
class OrderItemBase(SQLModel):
    product_id: int
    quantity: int
    price: float


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemRead(OrderItemBase):
    id: int
    product: Optional[dict] = None  # Will be populated with product details


# ============================================
# ORDER SCHEMAS
# ============================================
class OrderBase(SQLModel):
    customer_name: str
    customer_phone: str
    delivery_address: str


class OrderCreate(OrderBase):
    customer_email: Optional[str] = None
    payment_method: Optional[str] = None
    total_amount: Optional[float] = None
    notes: Optional[str] = None
    send_email_to_customer: bool = True
    send_email_to_admin: bool = True
    items: List[OrderItemCreate]


class OrderRead(OrderBase):
    id: int
    customer_email: Optional[str] = None
    status: str
    payment_method: Optional[str] = None
    payment_status: Optional[str] = None
    total_amount: Optional[float] = None
    total_price: float
    shipping_cost: Optional[float] = None
    created_at: datetime
    items: List[OrderItemRead]

    class Config:
        orm_mode = True
        
class OrderUpdate(SQLModel):
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    delivery_address: Optional[str] = None
    status: Optional[str] = None
    payment_status: Optional[str] = None


class PaymentVerification(SQLModel):
    mpesa_code: str
    phone_number: str

# ============================================
# INVOICE SCHEMAS
# ============================================
class InvoiceBase(SQLModel):
    order_id: int
    customer_id: int
    total_amount: float
    payment_method: Optional[str] = None
    remarks: Optional[str] = None


class InvoiceCreate(InvoiceBase):
    pass


class InvoiceRead(InvoiceBase):
    id: int
    invoice_date: datetime
    payment_status: str

    class Config:
        orm_mode = True


class InvoiceUpdate(SQLModel):
    payment_status: Optional[str] = None
    remarks: Optional[str] = None


# ============================================
# ADMIN USER SCHEMAS
# ============================================
class AdminUserBase(SQLModel):
    username: str


class AdminUserCreate(AdminUserBase):
    password: str


class AdminUserRead(AdminUserBase):
    id: int

    class Config:
        orm_mode = True
