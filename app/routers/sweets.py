from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app import models, schemas, auth
from app.database import get_db

router = APIRouter()

@router.post("", response_model=schemas.SweetResponse, status_code=status.HTTP_201_CREATED)
def create_sweet(
    sweet: schemas.SweetCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_admin_user)
):
    """Create a new sweet (Admin only)."""
    # Check if sweet name already exists
    db_sweet = db.query(models.Sweet).filter(models.Sweet.name == sweet.name).first()
    if db_sweet:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sweet with this name already exists"
        )
    
    db_sweet = models.Sweet(**sweet.dict())
    db.add(db_sweet)
    db.commit()
    db.refresh(db_sweet)
    return db_sweet

@router.get("", response_model=List[schemas.SweetResponse])
def get_sweets(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Get all sweets."""
    sweets = db.query(models.Sweet).all()
    return sweets

@router.get("/search", response_model=List[schemas.SweetResponse])
def search_sweets(
    name: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Search sweets by name, category, or price range."""
    query = db.query(models.Sweet)
    
    if name:
        query = query.filter(models.Sweet.name.ilike(f"%{name}%"))
    
    if category:
        query = query.filter(models.Sweet.category.ilike(f"%{category}%"))
    
    if min_price is not None:
        query = query.filter(models.Sweet.price >= min_price)
    
    if max_price is not None:
        query = query.filter(models.Sweet.price <= max_price)
    
    sweets = query.all()
    return sweets

@router.get("/{sweet_id}", response_model=schemas.SweetResponse)
def get_sweet(
    sweet_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Get a sweet by ID."""
    db_sweet = db.query(models.Sweet).filter(models.Sweet.id == sweet_id).first()
    if not db_sweet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sweet not found"
        )
    return db_sweet

@router.put("/{sweet_id}", response_model=schemas.SweetResponse)
def update_sweet(
    sweet_id: int,
    sweet_update: schemas.SweetUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_admin_user)
):
    """Update a sweet (Admin only)."""
    db_sweet = db.query(models.Sweet).filter(models.Sweet.id == sweet_id).first()
    if not db_sweet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sweet not found"
        )
    
    # Check if new name already exists (if name is being updated)
    if sweet_update.name and sweet_update.name != db_sweet.name:
        existing_sweet = db.query(models.Sweet).filter(models.Sweet.name == sweet_update.name).first()
        if existing_sweet:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sweet with this name already exists"
            )
    
    # Update sweet
    update_data = sweet_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_sweet, field, value)
    
    db.commit()
    db.refresh(db_sweet)
    return db_sweet

@router.delete("/{sweet_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sweet(
    sweet_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_admin_user)
):
    """Delete a sweet (Admin only)."""
    db_sweet = db.query(models.Sweet).filter(models.Sweet.id == sweet_id).first()
    if not db_sweet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sweet not found"
        )
    
    db.delete(db_sweet)
    db.commit()
    return None

@router.post("/{sweet_id}/purchase", response_model=schemas.SweetResponse)
def purchase_sweet(
    sweet_id: int,
    purchase: schemas.PurchaseRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Purchase a sweet, decreasing its quantity."""
    db_sweet = db.query(models.Sweet).filter(models.Sweet.id == sweet_id).first()
    if not db_sweet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sweet not found"
        )
    
    if db_sweet.quantity < purchase.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient quantity. Available: {db_sweet.quantity}, Requested: {purchase.quantity}"
        )
    
    db_sweet.quantity -= purchase.quantity
    db.commit()
    db.refresh(db_sweet)
    return db_sweet

@router.post("/{sweet_id}/restock", response_model=schemas.SweetResponse)
def restock_sweet(
    sweet_id: int,
    restock: schemas.RestockRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_admin_user)
):
    """Restock a sweet, increasing its quantity (Admin only)."""
    db_sweet = db.query(models.Sweet).filter(models.Sweet.id == sweet_id).first()
    if not db_sweet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sweet not found"
        )
    
    if restock.quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restock quantity must be greater than 0"
        )
    
    db_sweet.quantity += restock.quantity
    db.commit()
    db.refresh(db_sweet)
    return db_sweet

