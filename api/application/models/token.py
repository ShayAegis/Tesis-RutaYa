from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
    expiration: int = 0

class RefreshTokenRequest(BaseModel):
    refresh_token: str