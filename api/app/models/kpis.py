from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class KPIDeltas(BaseModel):
    orders: Optional[float] = None
    gmv: Optional[float] = None
    visits: Optional[float] = None
    views: Optional[float] = None
    conversion_rate: Optional[float] = None
    favorites: Optional[float] = None
    cart_adds: Optional[float] = None
    refunds: Optional[float] = None

class ShopMetrics(BaseModel):
    orders: int
    gmv: float
    visits: int
    views: int
    conversion_rate: float
    favorites: int
    cart_adds: int
    refunds: int
    deltas: KPIDeltas

class TrendPoint(BaseModel):
    date: str
    value: float

class TrendsResponse(BaseModel):
    revenue: list[TrendPoint]
    orders: list[TrendPoint]
    visits: list[TrendPoint]
    views: list[TrendPoint]

class FunnelMetrics(BaseModel):
    favorite_rate: float
    add_to_cart_rate: float
    conversion_rate: float

class TopListingItem(BaseModel):
    listing_id: int
    title: str
    views: int
    orders: int
    revenue: float
    etsy_url: str

class TopListings(BaseModel):
    by_views: list[TopListingItem]
    by_orders: list[TopListingItem]
    by_revenue: list[TopListingItem]

class ListingsResponse(BaseModel):
    items: list[TopListingItem]
    top: TopListings