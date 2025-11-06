# app/routers/product_router.py
import os
from fastapi import (
    APIRouter, Depends, HTTPException, status, UploadFile, File, Form
)
from sqlmodel import select, Session
from app.db.session import get_session
from app.models.models import Product, Category
from app.schemas.schemas import ProductRead, ProductUpdate

router = APIRouter(prefix="/products", tags=["Products"])

# Directory for storing uploaded product images
UPLOAD_DIR = "app/static/images"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# =====================================
# CREATE PRODUCT (with optional image)
# =====================================
@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(
    name: str = Form(...),
    description: str = Form(None),
    price: float = Form(...),
    stock_quantity: int = Form(...),
    category_id: int = Form(...),
    image: UploadFile = File(None),
    session: Session = Depends(get_session)
):
    """Create a new product with optional image upload"""
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    image_url = None
    if image:
        file_path = os.path.join(UPLOAD_DIR, image.filename)
        with open(file_path, "wb") as f:
            f.write(image.file.read())
        image_url = f"/static/images/{image.filename}"

    new_product = Product(
        name=name,
        description=description,
        price=price,
        stock_quantity=stock_quantity,
        category_id=category_id,
        image_url=image_url
    )

    session.add(new_product)
    session.commit()
    session.refresh(new_product)
    return new_product

# =====================================
# READ ALL PRODUCTS
# =====================================
@router.get("/", response_model=list[ProductRead])
def get_products(session: Session = Depends(get_session)):
    """Retrieve all products"""
    products = session.exec(select(Product)).all()
    return products


# =====================================
# READ SINGLE PRODUCT BY ID
# =====================================
@router.get("/{product_id}", response_model=ProductRead)
def get_product(product_id: int, session: Session = Depends(get_session)):
    """Retrieve a single product by its ID"""
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    return product


# =====================================
# UPDATE PRODUCT
# =====================================
@router.put("/{product_id}", response_model=ProductRead)
def update_product(
    product_id: int,
    product_update: ProductUpdate,
    session: Session = Depends(get_session)
):
    """Update an existing product"""
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )

    if product_update.category_id:
        new_category = session.get(Category, product_update.category_id)
        if not new_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="New category not found"
            )

    product_data = product_update.dict(exclude_unset=True)
    for key, value in product_data.items():
        setattr(product, key, value)

    session.add(product)
    session.commit()
    session.refresh(product)
    return product


# =====================================
# DELETE PRODUCT
# =====================================
@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
def delete_product(product_id: int, session: Session = Depends(get_session)):
    """Delete a product and its image (if exists)"""
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )

    # Delete associated image file if it exists
    if product.image_url:
        image_path = product.image_url.replace("/static/", "app/static/")
        if os.path.exists(image_path):
            os.remove(image_path)

    session.delete(product)
    session.commit()
    return {"detail": f"Product with ID {product_id} deleted successfully"}
