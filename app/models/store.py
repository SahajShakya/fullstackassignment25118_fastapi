from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import List, Optional

class Store3DModel(BaseModel):
    name: str
    glb_url: HttpUrl 
    position: List[float] = Field(..., description="XY position")
    size: List[float] = Field(..., description="scaling")
    entrance_order: int = Field(..., description="Order")

class Store(BaseModel):
    store_id: str
    name: str
    image_url: HttpUrl 
    models: List[Store3DModel] = Field(default_factory=list)
    max_users: int = Field(default=2)
    active_users: int = Field(default=0)
    installed_widget_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class StoreSelectRequest(BaseModel):
    user_id: str
    store_id: str

class StoreListRequest(BaseModel):
    user_id: str

class StoreResponse(BaseModel):
    store_id: str
    name: str
    image_url: HttpUrl
    models: List[Store3DModel]
    max_users: int
    active_users: int

class StoreListResponse(BaseModel):
    success: bool
    stores: List[StoreResponse] = []
    message: str = ""
