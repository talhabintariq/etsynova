from pydantic import BaseModel
from typing import Optional

class AuthStatus(BaseModel):
    connected: bool
    pending: bool
    shop_id: Optional[str] = None

class AuthConnect(BaseModel):
    auth_url: str

class AuthCallback(BaseModel):
    connected: bool
    shop_id: str

class AuthDisconnect(BaseModel):
    disconnected: bool