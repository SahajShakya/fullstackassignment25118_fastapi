from datetime import datetime
from bson.objectid import ObjectId
from typing import Optional, List
from models.widget import WidgetConfig
from models.analytics import AnalyticsEvent


class WidgetService:
    
    def __init__(self):
        self.db = None
    
    def set_db(self, db):
        self.db = db

    async def get_widget_by_domain(self, domain: str) -> Optional[dict]:
        widget = await self.db.widget_configs.find_one({
            "domain": domain,
            "is_active": True
        })
        return widget
    
    async def get_widget_by_id(self, widget_id: str) -> Optional[dict]:
        widget = await self.db.widget_configs.find_one({
            "_id": ObjectId(widget_id)
        })
        return widget
    
    async def get_widgets_by_store(self, store_id: str) -> List[dict]:
        widgets = await self.db.widget_configs.find({
            "store_id": store_id,
            "is_active": True
        }).to_list(length=None)
        return widgets
    
    async def get_all_widgets(self) -> List[dict]:
        """Get all active widgets from all stores"""
        widgets = await self.db.widget_configs.find({
            "is_active": True
        }).to_list(length=None)
        return widgets
    
    async def create_widget(
        self,
        store_id: str,
        domain: str,
        video_url: str,
        banner_text: str = ""
    ) -> str:
        widget = WidgetConfig(
            store_id=store_id,
            domain=domain,
            video_url=video_url,
            banner_text=banner_text,
            is_active=True
        )
        
        result = await self.db.widget_configs.insert_one(widget.to_dict())
        return str(result.inserted_id)
    
    async def update_widget(
        self,
        widget_id: str,
        video_url: Optional[str] = None,
        banner_text: Optional[str] = None,
        is_active: Optional[bool] = None,
        store_id: Optional[str] = None
    ) -> bool:
        update_data = {"updated_at": datetime.utcnow()}
        
        if video_url is not None:
            update_data["video_url"] = video_url
        if banner_text is not None:
            update_data["banner_text"] = banner_text
        if is_active is not None:
            update_data["is_active"] = is_active
        if store_id is not None:
            update_data["store_id"] = store_id
        
        result = await self.db.widget_configs.update_one(
            {"_id": ObjectId(widget_id)},
            {"$set": update_data}
        )
        
        return result.modified_count > 0
    
    async def delete_widget(self, widget_id: str) -> bool:
        result = await self.db.widget_configs.delete_one(
            {"_id": ObjectId(widget_id)}
        )
        return result.deleted_count > 0
    
    
    async def track_event(
        self,
        store_id: str,
        domain: str,
        event_type: str,
        user_agent: str = "",
        ip_address: str = ""
    ) -> str:
        
        event = AnalyticsEvent(
            store_id=store_id,
            domain=domain,
            event_type=event_type,
            user_agent=user_agent,
            ip_address=ip_address
        )
        
        result = await self.db.widget_analytics.insert_one(event.to_dict())
        return str(result.inserted_id)
    
    async def get_analytics(
        self,
        store_id: str,
        event_type: Optional[str] = None,
        limit: int = 100
    ) -> List[dict]:
        query = {"store_id": store_id}
        
        if event_type:
            query["event_type"] = event_type
        
        events = await self.db.widget_analytics.find(query).sort(
            "timestamp", -1
        ).limit(limit).to_list(length=None)
        
        return events
    
    async def get_analytics_by_domain(
        self,
        domain: str,
        event_type: Optional[str] = None,
        limit: int = 100
    ) -> List[dict]:
        query = {"domain": domain}
        
        if event_type:
            query["event_type"] = event_type
        
        events = await self.db.widget_analytics.find(query).sort(
            "timestamp", -1
        ).limit(limit).to_list(length=None)
        
        return events
    
    async def get_analytics_summary(
        self,
        store_id: str
    ) -> dict:
        
        pipeline = [
            {"$match": {"store_id": store_id}},
            {"$group": {
                "_id": "$event_type",
                "count": {"$sum": 1}
            }}
        ]
        
        results = await self.db.widget_analytics.aggregate(pipeline).to_list(None)
        
        summary = {
            "page_view": 0,
            "video_loaded": 0,
            "link_clicked": 0
        }
        
        for result in results:
            event_type = result["_id"]
            count = result["count"]
            summary[event_type] = count
        return summary


widget_service = WidgetService()
