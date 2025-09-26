from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
import time
import logging

# Load environment variables
load_dotenv()

# Import routers
from app.routers import auth, metrics, reports, health, inbox

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="EtsyNova API",
    description="Etsy Store Analytics Dashboard API with AI-powered insights",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware with environment configuration
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:3001").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    # Filter out PII from logs
    safe_path = request.url.path
    if "token" in safe_path.lower() or "key" in safe_path.lower():
        safe_path = "[REDACTED]"

    logger.info(
        f"Method: {request.method} | Path: {safe_path} | "
        f"Status: {response.status_code} | Duration: {process_time:.4f}s"
    )
    return response

# Include routers
app.include_router(auth.router)
app.include_router(metrics.router)
app.include_router(reports.router)
app.include_router(health.router)
app.include_router(inbox.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to EtsyNova API",
        "version": "1.0.0",
        "mock_mode": os.getenv("MOCK_MODE", "false") == "true",
        "llm_provider": os.getenv("LLM_PROVIDER", "none"),
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "auth": "/auth",
            "metrics": "/metrics",
            "reports": "/reports",
            "inbox": "/inbox"
        }
    }

# Legacy endpoints for backward compatibility
@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Legacy endpoint - redirects to /metrics/shop"""
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
    """Legacy endpoint - redirects to /metrics/listings"""
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
