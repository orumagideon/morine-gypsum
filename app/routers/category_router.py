# app/routers/category_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select, Session
from app.db.session import get_session
from app.models.models import Category
from app.schemas.schemas import CategoryCreate, CategoryRead, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["Categories"])

# =====================================
# CREATE CATEGORY
# =====================================
@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(category: CategoryCreate, session: Session = Depends(get_session)):
    existing_category = session.exec(
        select(Category).where(Category.name == category.name)
    ).first()
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category already exists"
        )

    new_category = Category(
        name=category.name,
        description=category.description,
        parent_id=category.parent_id
    )
    session.add(new_category)
    session.commit()
    session.refresh(new_category)
    return new_category


# =====================================
# READ ALL CATEGORIES
# =====================================
@router.get("/", response_model=list[CategoryRead], status_code=status.HTTP_200_OK)
def get_categories(session: Session = Depends(get_session)):
    categories = session.exec(select(Category)).all()
    return categories


# =====================================
# READ SINGLE CATEGORY BY ID
# =====================================
@router.get("/{category_id}", response_model=CategoryRead, status_code=status.HTTP_200_OK)
def get_category(category_id: int, session: Session = Depends(get_session)):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found"
        )
    return category


# =====================================
# UPDATE CATEGORY
# =====================================
@router.put("/{category_id}", response_model=CategoryRead, status_code=status.HTTP_200_OK)
def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    session: Session = Depends(get_session)
):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found"
        )

    # Validate parent_id if provided
    if category_update.parent_id is not None:
        if category_update.parent_id == category_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category cannot be its own parent"
            )
        # Handle None or empty string as no parent
        if category_update.parent_id == 0 or category_update.parent_id == "":
            category_update.parent_id = None
        elif category_update.parent_id:
            parent = session.get(Category, category_update.parent_id)
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Parent category not found"
                )
    
    category_data = category_update.dict(exclude_unset=True)
    # Convert empty string to None for parent_id
    if "parent_id" in category_data and category_data["parent_id"] == "":
        category_data["parent_id"] = None
    for key, value in category_data.items():
        setattr(category, key, value)

    session.add(category)
    session.commit()
    session.refresh(category)
    return category


# =====================================
# DELETE CATEGORY
# =====================================
@router.delete("/{category_id}", status_code=status.HTTP_200_OK)
def delete_category(category_id: int, session: Session = Depends(get_session)):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found"
        )

    session.delete(category)
    session.commit()
    return {"detail": f"Category with ID {category_id} deleted successfully"}
