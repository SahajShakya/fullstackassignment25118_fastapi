from datetime import datetime
from typing import Optional
from bson import ObjectId


class WidgetConfig:
    """Widget configuration stored in MongoDB"""
    
    def __init__(
        self,
        store_id: str,
        domain: str,
        video_url: str,
        banner_text: str = "",
        is_active: bool = True,
        _id: Optional[ObjectId] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self._id = _id or ObjectId()
        self.store_id = store_id  # Keep as string, not ObjectId
        self.domain = domain
        self.video_url = video_url
        self.banner_text = banner_text
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for MongoDB storage"""
        return {
            "_id": self._id,
            "store_id": self.store_id,
            "domain": self.domain,
            "video_url": self.video_url,
            "banner_text": self.banner_text,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    @staticmethod
    def from_dict(data: dict) -> "WidgetConfig":
        return WidgetConfig(
            store_id=str(data.get("store_id")),
            domain=data.get("domain"),
            video_url=data.get("video_url"),
            banner_text=data.get("banner_text", ""),
            is_active=data.get("is_active", True),
            _id=data.get("_id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
