from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse
from app.models.auth import AuthStatus, AuthConnect, AuthCallback, AuthDisconnect
from app.services.etsy_client import EtsyClient
import os

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/etsy/connect", response_model=AuthConnect)
async def connect_etsy():
    """Initiate Etsy OAuth connection"""
    etsy_client = EtsyClient()
    auth_url = await etsy_client.get_auth_url()
    return AuthConnect(auth_url=auth_url)

@router.get("/etsy/callback", response_model=AuthCallback)
async def etsy_callback(code: str, state: str):
    """Handle Etsy OAuth callback"""
    etsy_client = EtsyClient()
    shop_data = await etsy_client.handle_callback(code, state)
    return AuthCallback(connected=True, shop_id=shop_data["shop_id"])

@router.get("/status", response_model=AuthStatus)
async def auth_status():
    """Get current authentication status"""
    # In mock mode, return demo status
    mock_mode = os.getenv("MOCK_MODE", "false") == "true"
    if mock_mode:
        return AuthStatus(connected=False, pending=True, shop_id=None)

    # TODO: Check actual session/token status
    return AuthStatus(connected=False, pending=False, shop_id=None)

@router.post("/etsy/disconnect", response_model=AuthDisconnect)
async def disconnect_etsy():
    """Disconnect from Etsy"""
    # TODO: Clear session/tokens
    return AuthDisconnect(disconnected=True)