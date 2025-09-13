from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    return {"ok": True}