"""User model for authentication"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class User(BaseModel):
    username: str = Field(..., min_length=3, description="Unique username")
    password: str = Field(..., min_length=6, description="Hashed password")
    display_name: str = Field(..., description="Display name in store")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = Field(None)
    active: bool = Field(default=True)
