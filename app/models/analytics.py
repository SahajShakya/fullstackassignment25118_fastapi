from datetime import datetime
from typing import Optional
from bson import ObjectId


class AnalyticsEvent:
    PAGE_VIEW = "page_view"
    VIDEO_LOADED = "video_loaded"
    LINK_CLICKED = "link_clicked"
    
    VALID_EVENTS = {PAGE_VIEW, VIDEO_LOADED, LINK_CLICKED}
    
    def __init__(
        self,
        store_id: str,
        domain: str,
        event_type: str,
        user_agent: str = "",
        ip_address: str = "",
        _id: Optional[ObjectId] = None,
        timestamp: Optional[datetime] = None,
    ):
        self._id = _id or ObjectId()
        self.store_id = store_id  # Keep as string, not ObjectId
        self.domain = domain
        
        if event_type not in self.VALID_EVENTS:
            raise ValueError(f"Invalid event_type. Must be one of: {self.VALID_EVENTS}")
        
        self.event_type = event_type
        self.user_agent = user_agent
        self.ip_address = ip_address
        self.timestamp = timestamp or datetime.utcnow()
    
    def to_dict(self) -> dict:
        return {
            "_id": self._id,
            "store_id": self.store_id,
            "domain": self.domain,
            "event_type": self.event_type,
            "user_agent": self.user_agent,
            "ip_address": self.ip_address,
            "timestamp": self.timestamp,
        }
    
    @staticmethod
    def from_dict(data: dict) -> "AnalyticsEvent":
        return AnalyticsEvent(
            store_id=str(data.get("store_id")),
            domain=data.get("domain"),
            event_type=data.get("event_type"),
            user_agent=data.get("user_agent", ""),
            ip_address=data.get("ip_address", ""),
            _id=data.get("_id"),
            timestamp=data.get("timestamp"),
        )
