"""Product CRUD endpoints."""

from typing import Optional
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..messaging import ProductEventPublisher, get_event_publisher
from ..models import Product
from ..schemas import (
    InventoryUpdate,
    PaginatedResponse,
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.get("", response_model=PaginatedResponse)
def list_products(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    category: Optional[str] = None,
    active_only: bool = True,
    db: Session = Depends(get_db),
) -> PaginatedResponse:
    """List products with pagination."""
    query = db.query(Product)

    if active_only:
        query = query.filter(Product.is_active == True)

    if category:
        query = query.filter(Product.category == category)

    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return PaginatedResponse(
        items=[ProductResponse.model_validate(p) for p in items],
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: UUID, db: Session = Depends(get_db)) -> ProductResponse:
    """Get a product by ID."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return ProductResponse.model_validate(product)


@router.get("/sku/{sku}", response_model=ProductResponse)
def get_product_by_sku(sku: str, db: Session = Depends(get_db)) -> ProductResponse:
    """Get a product by SKU."""
    product = db.query(Product).filter(Product.sku == sku).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return ProductResponse.model_validate(product)


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product_in: ProductCreate, db: Session = Depends(get_db)) -> ProductResponse:
    """Create a new product."""
    # Check for duplicate SKU
    existing = db.query(Product).filter(Product.sku == product_in.sku).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Product with SKU '{product_in.sku}' already exists",
        )

    product = Product(**product_in.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)

    logger.info("product_created", product_id=str(product.id), sku=product.sku)

    return ProductResponse.model_validate(product)


@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: UUID, product_in: ProductUpdate, db: Session = Depends(get_db)
) -> ProductResponse:
    """Update a product."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    update_data = product_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)

    logger.info("product_updated", product_id=str(product.id), fields=list(update_data.keys()))

    return ProductResponse.model_validate(product)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: UUID, db: Session = Depends(get_db)) -> None:
    """Soft delete a product (sets is_active=False)."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    product.is_active = False
    db.commit()

    logger.info("product_deleted", product_id=str(product.id))


@router.post("/{product_id}/inventory", response_model=ProductResponse)
def update_inventory(
    product_id: UUID,
    inventory_update: InventoryUpdate,
    db: Session = Depends(get_db),
    event_publisher: ProductEventPublisher = Depends(get_event_publisher),
    x_correlation_id: Optional[str] = Header(None),
) -> ProductResponse:
    """Update product inventory and publish event."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    previous_quantity = int(product.quantity)
    new_quantity = previous_quantity + inventory_update.quantity_change

    if new_quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient inventory. Current: {previous_quantity}, requested change: {inventory_update.quantity_change}",
        )

    product.quantity = new_quantity
    db.commit()
    db.refresh(product)

    logger.info(
        "inventory_updated",
        product_id=str(product.id),
        previous_quantity=previous_quantity,
        new_quantity=new_quantity,
        reason=inventory_update.reason,
    )

    # Publish inventory.updated event to RabbitMQ
    event_publisher.publish_inventory_updated(
        product_id=str(product.id),
        sku=product.sku,
        previous_quantity=previous_quantity,
        new_quantity=new_quantity,
        reason=inventory_update.reason,
        correlation_id=x_correlation_id,
    )

    return ProductResponse.model_validate(product)
