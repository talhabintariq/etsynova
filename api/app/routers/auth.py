from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from app.models.auth import AuthStatus, AuthConnect, AuthCallback, AuthDisconnect
from app.models.inbox import MockEmailData
from app.services.etsy_client import EtsyClient
from google.auth.transport.requests import Request as GoogleRequest
from google_auth_oauthlib.flow import Flow
import os
import json
from datetime import datetime, timedelta

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

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")

# Gmail OAuth Scopes
GMAIL_SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
]

@router.post("/google/connect")
async def connect_google():
    """Start Google OAuth flow for Gmail access"""
    # Check if in mock mode
    mock_mode = os.getenv("MOCK_MODE", "false") == "true"
    if mock_mode:
        return {
            "auth_url": "mock://google-oauth",
            "message": "Mock mode: Gmail connection will be simulated"
        }

    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=500,
            detail="Google OAuth credentials not configured"
        )

    # Create OAuth flow
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [GOOGLE_REDIRECT_URI]
            }
        },
        scopes=GMAIL_SCOPES
    )
    flow.redirect_uri = GOOGLE_REDIRECT_URI

    # Generate authorization URL
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'  # Force consent to ensure refresh token
    )

    return {
        "auth_url": authorization_url,
        "state": state
    }

@router.get("/google/callback")
async def google_callback(request: Request, code: str = None, state: str = None, error: str = None):
    """Handle Google OAuth callback"""

    # Handle OAuth errors
    if error:
        raise HTTPException(
            status_code=400,
            detail=f"Google OAuth error: {error}"
        )

    if not code:
        raise HTTPException(
            status_code=400,
            detail="Authorization code not provided"
        )

    # Check if in mock mode
    mock_mode = os.getenv("MOCK_MODE", "false") == "true"
    if mock_mode:
        return {
            "connected": True,
            "email": "seller@example.com",
            "provider": "google",
            "message": "Mock Gmail connection successful"
        }

    try:
        # Complete OAuth flow
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [GOOGLE_REDIRECT_URI]
                }
            },
            scopes=GMAIL_SCOPES,
            state=state
        )
        flow.redirect_uri = GOOGLE_REDIRECT_URI

        # Exchange code for token
        flow.fetch_token(code=code)

        # Get user info
        credentials = flow.credentials

        # TODO: Store encrypted tokens in database
        # For now, return success with mock data

        return {
            "connected": True,
            "email": "seller@example.com",  # TODO: Get from Google API
            "provider": "google",
            "tokens_stored": True,
            "scopes": GMAIL_SCOPES
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to complete Google OAuth: {str(e)}"
        )

@router.get("/google/status")
async def google_auth_status():
    """Get Gmail connection status"""
    mock_mode = os.getenv("MOCK_MODE", "false") == "true"

    if mock_mode:
        return MockEmailData.get_mock_oauth_status()

    # TODO: Check database for stored tokens and their validity
    return {
        "connected": False,
        "email": None,
        "provider": "google",
        "last_sync": None,
        "messages_count": 0
    }

@router.post("/google/disconnect")
async def disconnect_google():
    """Disconnect Gmail integration"""
    # TODO: Revoke tokens and clear from database

    return {
        "disconnected": True,
        "provider": "google",
        "message": "Gmail connection removed"
    }