from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ListingImage(BaseModel):
    url: str
    alt_text: Optional[str] = None

class Listing(BaseModel):
    listing_id: int
    title: str
    description: Optional[str] = None
    price: float
    currency_code: str = "USD"
    quantity: int
    views: int = 0
    favorites: int = 0
    orders: int = 0
    revenue: float = 0.0
    created_timestamp: datetime
    last_modified_timestamp: datetime
    state: str  # active, inactive, draft, expired, etc.
    images: List[ListingImage] = []
    tags: List[str] = []
    materials: List[str] = []
    etsy_url: str

class ListingStats(BaseModel):
    listing_id: int
    views: int
    favorites: int
    orders: int
    revenue: float
    conversion_rate: float