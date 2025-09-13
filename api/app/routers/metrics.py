from fastapi import APIRouter, Query
from typing import Optional
from app.models.kpis import ShopMetrics, ListingsResponse, TrendsResponse, FunnelMetrics
from app.services.etsy_client import EtsyClient
from app.services.aggregator import MetricsAggregator
import os

router = APIRouter(prefix="/metrics", tags=["metrics"])

@router.get("/shop", response_model=ShopMetrics)
async def get_shop_metrics(
    shop_id: str = Query(..., description="Shop ID"),
    from_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    to_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """Get shop-level metrics and KPIs"""
    etsy_client = EtsyClient()
    aggregator = MetricsAggregator()

    raw_data = await etsy_client.get_shop_stats(shop_id, from_date, to_date)
    metrics = aggregator.aggregate_shop_metrics(raw_data)

    return metrics

@router.get("/listings", response_model=ListingsResponse)
async def get_listings_metrics(
    shop_id: str = Query(..., description="Shop ID"),
    from_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    to_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(50, description="Number of listings to return")
):
    """Get listings metrics and top performers"""
    etsy_client = EtsyClient()
    aggregator = MetricsAggregator()

    raw_data = await etsy_client.get_listings_stats(shop_id, from_date, to_date, limit)
    listings = aggregator.aggregate_listings_metrics(raw_data)

    return listings

@router.get("/trends", response_model=TrendsResponse)
async def get_trends(
    shop_id: str = Query(..., description="Shop ID"),
    from_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    to_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    series: str = Query("revenue,orders,visits,views", description="Comma-separated series names")
):
    """Get time series trends data"""
    etsy_client = EtsyClient()
    aggregator = MetricsAggregator()

    series_list = [s.strip() for s in series.split(",")]
    raw_data = await etsy_client.get_trends_data(shop_id, from_date, to_date, series_list)
    trends = aggregator.aggregate_trends(raw_data, series_list)

    return trends

@router.get("/funnel", response_model=FunnelMetrics)
async def get_funnel_metrics(
    shop_id: str = Query(..., description="Shop ID"),
    from_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    to_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """Get conversion funnel metrics"""
    etsy_client = EtsyClient()
    aggregator = MetricsAggregator()

    raw_data = await etsy_client.get_funnel_stats(shop_id, from_date, to_date)
    funnel = aggregator.aggregate_funnel_metrics(raw_data)

    return funnel