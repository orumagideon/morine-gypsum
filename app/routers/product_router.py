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
    category_id: int = Form(None),
    image: UploadFile = File(None),
    session: Session = Depends(get_session)
):
    """Create a new product with optional image upload and category"""
    # Validate category if provided
    category_id_value = None
    if category_id:
        category = session.get(Category, category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        category_id_value = category_id

    image_url = None
    if image and image.filename:
        # Generate unique filename to avoid conflicts
        import uuid
        file_ext = os.path.splitext(image.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        with open(file_path, "wb") as f:
            f.write(image.file.read())
        image_url = f"/static/images/{unique_filename}"

    new_product = Product(
        name=name,
        description=description,
        price=price,
        stock_quantity=stock_quantity,
        category_id=category_id_value,
        image_url=image_url
    )

    session.add(new_product)
    session.commit()
    session.refresh(new_product)
    
    # Load category relationship
    if new_product.category_id:
        new_product.category = session.get(Category, new_product.category_id)
    
    return new_product

# =====================================
# READ ALL PRODUCTS (with filtering and search)
# =====================================
@router.get("/", response_model=list[ProductRead])
def get_products(
    category_id: int = None,
    search: str = None,
    session: Session = Depends(get_session)
):
    """Retrieve all products with optional category filtering and search"""
    query = select(Product)
    
    # Filter by category if provided
    if category_id:
        query = query.where(Product.category_id == category_id)
    
    # Search by name or description if provided
    if search:
        search_term = f"%{search.lower()}%"
        query = query.where(
            (Product.name.ilike(search_term)) | 
            (Product.description.ilike(search_term))
        )
    
    products = session.exec(query).all()
    
    # Load category relationships
    for product in products:
        if product.category_id:
            product.category = session.get(Category, product.category_id)
    
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
    
    # Load category relationship
    if product.category_id:
        product.category = session.get(Category, product.category_id)
    
    return product


# =====================================
# UPDATE PRODUCT
# =====================================
@router.put("/{product_id}", response_model=ProductRead)
def update_product(
    product_id: int,
    name: str = Form(None),
    description: str = Form(None),
    price: float = Form(None),
    stock_quantity: int = Form(None),
    category_id: str = Form(None),  # Changed to str to handle empty strings
    image: UploadFile = File(None),
    session: Session = Depends(get_session)
):
    """Update an existing product with optional image upload"""
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )

    # Update category if provided
    if category_id is not None:
        if category_id == "" or category_id == "0":
            # Clear category
            product.category_id = None
        else:
            try:
                cat_id = int(category_id)
                new_category = session.get(Category, cat_id)
                if not new_category:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Category not found"
                    )
                product.category_id = cat_id
            except (ValueError, TypeError):
                # Invalid category_id, skip update
                pass

    # Update other fields
    if name is not None:
        product.name = name
    if description is not None:
        product.description = description
    if price is not None:
        product.price = price
    if stock_quantity is not None:
        product.stock_quantity = stock_quantity

    # Handle image upload
    if image and image.filename:
        # Delete old image if exists
        if product.image_url:
            old_image_path = product.image_url.replace("/static/", "app/static/")
            if os.path.exists(old_image_path):
                os.remove(old_image_path)
        
        # Generate unique filename to avoid conflicts
        import uuid
        file_ext = os.path.splitext(image.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        with open(file_path, "wb") as f:
            f.write(image.file.read())
        product.image_url = f"/static/images/{unique_filename}"

    session.add(product)
    session.commit()
    session.refresh(product)
    
    # Load category relationship
    if product.category_id:
        product.category = session.get(Category, product.category_id)
    
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
