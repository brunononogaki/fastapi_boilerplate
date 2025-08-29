from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description='Username')
    password: str = Field(..., min_length=6, description='Password')


class TokenResponse(BaseModel):
    access_token: str = Field(..., description='JWT access token')
    token_type: str = Field(default='bearer', description='Token type')
    expires_in: int = Field(..., description='Token expiration time in minutes')


class TokenData(BaseModel):
    username: str = Field(..., description='Username from token')
    user_id: str = Field(..., description='User ID from token')
