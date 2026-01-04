"""Pydantic schemas for API request/response models."""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    """Base product schema."""

    sku: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0, decimal_places=2)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    quantity: int = Field(default=0, ge=0)
    category: Optional[str] = Field(default=None, max_length=100)
    image_url: Optional[str] = Field(default=None, max_length=500)


class ProductCreate(ProductBase):
    """Schema for creating a product."""

    pass


class ProductUpdate(BaseModel):
    """Schema for updating a product."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(default=None, gt=0, decimal_places=2)
    quantity: Optional[int] = Field(default=None, ge=0)
    category: Optional[str] = Field(default=None, max_length=100)
    is_active: Optional[bool] = None
    image_url: Optional[str] = Field(default=None, max_length=500)


class ProductResponse(ProductBase):
    """Schema for product response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime


class InventoryUpdate(BaseModel):
    """Schema for inventory adjustment."""

    quantity_change: int = Field(..., description="Positive to add, negative to subtract")
    reason: str = Field(..., min_length=1, max_length=200)


class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""

    items: list[ProductResponse]
    total: int
    page: int
    page_size: int
    pages: int
