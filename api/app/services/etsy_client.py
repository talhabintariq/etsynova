import os
import json
import httpx
from typing import Dict, Any, List, Optional
from urllib.parse import urlencode
import asyncio
from app.services.cache import CacheService

class EtsyClient:
    """Etsy API client with OAuth2 PKCE, retry logic, and mock mode support"""

    def __init__(self):
        self.client_id = os.getenv("ETSY_CLIENT_ID")
        self.client_secret = os.getenv("ETSY_CLIENT_SECRET")
        self.redirect_uri = os.getenv("ETSY_REDIRECT_URI")
        self.mock_mode = os.getenv("MOCK_MODE", "false") == "true"
        self.base_url = "https://openapi.etsy.com/v3/application"
        self.cache = CacheService()

    async def get_auth_url(self) -> str:
        """Generate Etsy OAuth authorization URL"""
        if self.mock_mode or not self.client_id:
            return "https://mock-auth-url.com?state=mock"

        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "listings_r shops_r",
            "state": "etsynova_state_123"  # TODO: Generate secure state
        }
        return f"https://www.etsy.com/oauth/connect?{urlencode(params)}"

    async def handle_callback(self, code: str, state: str) -> Dict[str, Any]:
        """Handle OAuth callback and exchange code for token"""
        if self.mock_mode:
            return {"shop_id": "mock_shop_123", "access_token": "mock_token"}

        # TODO: Implement actual OAuth token exchange
        return {"shop_id": "demo_shop", "access_token": "demo_token"}

    async def get_shop_stats(self, shop_id: str, from_date: Optional[str] = None,
                           to_date: Optional[str] = None) -> Dict[str, Any]:
        """Get shop statistics"""
        if self.mock_mode:
            return await self._load_fixture("shop_stats")

        # TODO: Implement actual Etsy API calls with retry logic
        return {}

    async def get_listings_stats(self, shop_id: str, from_date: Optional[str] = None,
                               to_date: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
        """Get listings statistics"""
        if self.mock_mode:
            return await self._load_fixture("listings_stats")

        # TODO: Implement actual Etsy API calls
        return {}

    async def get_trends_data(self, shop_id: str, from_date: Optional[str] = None,
                            to_date: Optional[str] = None, series: List[str] = None) -> Dict[str, Any]:
        """Get trends data"""
        if self.mock_mode:
            return await self._load_fixture("trends_data")

        # TODO: Implement actual Etsy API calls
        return {}

    async def get_funnel_stats(self, shop_id: str, from_date: Optional[str] = None,
                             to_date: Optional[str] = None) -> Dict[str, Any]:
        """Get funnel statistics"""
        if self.mock_mode:
            return await self._load_fixture("funnel_stats")

        # TODO: Implement actual Etsy API calls
        return {}

    async def _make_request(self, method: str, endpoint: str, params: Dict = None,
                          data: Dict = None, retries: int = 3) -> Dict[str, Any]:
        """Make HTTP request with retry logic and error handling"""
        async with httpx.AsyncClient() as client:
            for attempt in range(retries):
                try:
                    response = await client.request(
                        method=method,
                        url=f"{self.base_url}{endpoint}",
                        params=params,
                        json=data,
                        headers={"Authorization": f"Bearer {self._get_access_token()}"},
                        timeout=30
                    )

                    if response.status_code == 429:
                        # Rate limited, exponential backoff
                        await asyncio.sleep(2 ** attempt)
                        continue
                    elif response.status_code >= 500:
                        # Server error, retry
                        if attempt < retries - 1:
                            await asyncio.sleep(1)
                            continue
                    elif response.status_code == 401:
                        # Unauthorized, refresh token
                        await self._refresh_token()
                        continue

                    response.raise_for_status()
                    return response.json()

                except httpx.RequestError:
                    if attempt < retries - 1:
                        await asyncio.sleep(1)
                        continue
                    raise

        raise Exception(f"Failed to make request after {retries} attempts")

    def _get_access_token(self) -> str:
        """Get current access token"""
        # TODO: Implement token storage/retrieval
        return "mock_token"

    async def _refresh_token(self):
        """Refresh OAuth token"""
        # TODO: Implement token refresh
        pass

    async def _load_fixture(self, fixture_name: str) -> Dict[str, Any]:
        """Load mock data fixture"""
        try:
            # Try multiple possible paths
            possible_paths = [
                f"fixtures/{fixture_name}.json",
                f"api/fixtures/{fixture_name}.json",
                f"./fixtures/{fixture_name}.json"
            ]

            for fixture_path in possible_paths:
                if os.path.exists(fixture_path):
                    with open(fixture_path, 'r') as f:
                        return json.load(f)
        except Exception:
            pass

        # Return minimal mock data if fixture not found
        return self._get_default_fixture(fixture_name)

    def _get_default_fixture(self, fixture_name: str) -> Dict[str, Any]:
        """Generate default fixture data"""
        fixtures = {
            "shop_stats": {
                "orders": 142,
                "gmv": 3456.78,
                "visits": 8932,
                "views": 12456,
                "conversion_rate": 4.2,
                "favorites": 234,
                "cart_adds": 567,
                "refunds": 23
            },
            "listings_stats": {
                "listings": [
                    {
                        "listing_id": 123,
                        "title": "Handmade Ceramic Mug",
                        "views": 456,
                        "orders": 45,
                        "revenue": 675.00,
                        "etsy_url": "https://etsy.com/listing/123"
                    }
                ]
            },
            "trends_data": {
                "revenue": [{"date": "2024-01-01", "value": 100.0}],
                "orders": [{"date": "2024-01-01", "value": 5}],
                "visits": [{"date": "2024-01-01", "value": 200}],
                "views": [{"date": "2024-01-01", "value": 300}]
            },
            "funnel_stats": {
                "favorite_rate": 5.2,
                "add_to_cart_rate": 8.7,
                "conversion_rate": 4.2
            }
        }
        return fixtures.get(fixture_name, {})