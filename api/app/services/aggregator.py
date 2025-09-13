from typing import Dict, Any, List
from app.models.kpis import ShopMetrics, KPIDeltas, ListingsResponse, TrendsResponse, FunnelMetrics, TopListingItem, TopListings, TrendPoint

class MetricsAggregator:
    """Service for aggregating and transforming raw Etsy data into structured metrics"""

    def aggregate_shop_metrics(self, raw_data: Dict[str, Any]) -> ShopMetrics:
        """Aggregate raw shop data into structured metrics"""
        deltas = KPIDeltas()  # TODO: Calculate actual deltas

        return ShopMetrics(
            orders=raw_data.get("orders", 0),
            gmv=raw_data.get("gmv", 0.0),
            visits=raw_data.get("visits", 0),
            views=raw_data.get("views", 0),
            conversion_rate=raw_data.get("conversion_rate", 0.0),
            favorites=raw_data.get("favorites", 0),
            cart_adds=raw_data.get("cart_adds", 0),
            refunds=raw_data.get("refunds", 0),
            deltas=deltas
        )

    def aggregate_listings_metrics(self, raw_data: Dict[str, Any]) -> ListingsResponse:
        """Aggregate raw listings data into structured metrics"""
        listings = raw_data.get("listings", [])
        items = []

        for listing in listings:
            item = TopListingItem(
                listing_id=listing.get("listing_id", 0),
                title=listing.get("title", ""),
                views=listing.get("views", 0),
                orders=listing.get("orders", 0),
                revenue=listing.get("revenue", 0.0),
                etsy_url=listing.get("etsy_url", "")
            )
            items.append(item)

        # Create top listings by different metrics
        top_by_views = sorted(items, key=lambda x: x.views, reverse=True)[:5]
        top_by_orders = sorted(items, key=lambda x: x.orders, reverse=True)[:5]
        top_by_revenue = sorted(items, key=lambda x: x.revenue, reverse=True)[:5]

        top = TopListings(
            by_views=top_by_views,
            by_orders=top_by_orders,
            by_revenue=top_by_revenue
        )

        return ListingsResponse(items=items, top=top)

    def aggregate_trends(self, raw_data: Dict[str, Any], series_list: List[str]) -> TrendsResponse:
        """Aggregate raw trends data into time series"""
        trends = TrendsResponse(
            revenue=[],
            orders=[],
            visits=[],
            views=[]
        )

        for series_name in series_list:
            if series_name in raw_data and hasattr(trends, series_name):
                series_data = raw_data[series_name]
                trend_points = [
                    TrendPoint(date=point["date"], value=point["value"])
                    for point in series_data
                ]
                setattr(trends, series_name, trend_points)

        return trends

    def aggregate_funnel_metrics(self, raw_data: Dict[str, Any]) -> FunnelMetrics:
        """Aggregate raw funnel data into structured metrics"""
        return FunnelMetrics(
            favorite_rate=raw_data.get("favorite_rate", 0.0),
            add_to_cart_rate=raw_data.get("add_to_cart_rate", 0.0),
            conversion_rate=raw_data.get("conversion_rate", 0.0)
        )

    def calculate_deltas(self, current: Dict[str, Any], previous: Dict[str, Any]) -> KPIDeltas:
        """Calculate percentage deltas between current and previous periods"""
        deltas = KPIDeltas()

        for key in ["orders", "gmv", "visits", "views", "conversion_rate", "favorites", "cart_adds", "refunds"]:
            current_val = current.get(key, 0)
            previous_val = previous.get(key, 0)

            if previous_val > 0:
                delta = ((current_val - previous_val) / previous_val) * 100
                setattr(deltas, key, round(delta, 2))

        return deltas