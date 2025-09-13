from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os

app = FastAPI(
    title="EtsyNova API",
    description="Etsy Store Analytics Dashboard API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Welcome to EtsyNova API",
        "version": "1.0.0",
        "mock_mode": os.getenv("MOCK_MODE", "false") == "true"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "etsynova-api"}

# Mock data endpoint for testing
@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    if os.getenv("MOCK_MODE", "false") == "true":
        return {
            "total_orders": 142,
            "total_revenue": 3456.78,
            "total_views": 8932,
            "conversion_rate": 4.2,
            "period": "last_30_days"
        }
    else:
        return {"message": "Connect your Etsy store to view real data"}

@app.get("/api/products/top")
async def get_top_products():
    if os.getenv("MOCK_MODE", "false") == "true":
        return {
            "products": [
                {"name": "Handmade Ceramic Mug", "sales": 45, "revenue": 675.00},
                {"name": "Vintage Style Poster", "sales": 32, "revenue": 480.00},
                {"name": "Custom Jewelry Box", "sales": 28, "revenue": 1120.00},
                {"name": "Organic Soap Set", "sales": 25, "revenue": 375.00},
                {"name": "Knitted Winter Scarf", "sales": 22, "revenue": 440.00}
            ]
        }
    else:
        return {"message": "Connect your Etsy store to view real data"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
