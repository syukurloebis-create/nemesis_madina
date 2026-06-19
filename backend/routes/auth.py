from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/login")
async def login(request: LoginRequest):
    # TEMPORARY BYPASS - Accept any credentials
    return LoginResponse(access_token="dev-token-bypass-auth")
