import strawberry
from typing import Optional, List
from datetime import datetime
import db.mongo as mongo_module
from services.widget_service import widget_service


@strawberry.type
class WidgetConfigType:
    """Widget configuration GraphQL type"""
    id: str
    store_id: str = strawberry.field(name="storeId")
    domain: str
    video_url: str = strawberry.field(name="videoUrl")
    banner_text: str = strawberry.field(name="bannerText")
    is_active: bool = strawberry.field(name="isActive")
    created_at: datetime = strawberry.field(name="createdAt")
    updated_at: datetime = strawberry.field(name="updatedAt")


@strawberry.type
class AnalyticsEventType:
    """Analytics event GraphQL type"""
    id: str
    store_id: str
    domain: str
    event_type: str
    user_agent: str
    ip_address: str
    timestamp: datetime


@strawberry.type
class AnalyticsSummaryType:
    """Analytics summary statistics"""
    page_view: int = strawberry.field(name="pageView")
    video_loaded: int = strawberry.field(name="videoLoaded")
    link_clicked: int = strawberry.field(name="linkClicked")


@strawberry.type
class WidgetQuery:
    @strawberry.field
    async def get_widget_by_domain(self, domain: str) -> Optional[WidgetConfigType]:
        """Get widget configuration by domain (PUBLIC - no auth required)"""
        db = mongo_module.db
        widget_service.set_db(db)
        
        widget = await widget_service.get_widget_by_domain(domain)
        
        if not widget:
            return None
        
        return WidgetConfigType(
            id=str(widget["_id"]),
            store_id=str(widget["store_id"]),
            domain=widget["domain"],
            video_url=widget["video_url"],
            banner_text=widget.get("banner_text", ""),
            is_active=widget["is_active"],
            created_at=widget["created_at"],
            updated_at=widget["updated_at"],
        )
    
    @strawberry.field
    async def get_widgets_by_store(
        self,
        store_id: str,
        info=None
    ) -> List[WidgetConfigType]:
        """Get all widgets for a store (requires auth)"""
        # TODO: Add auth check
        db = mongo_module.db
        widget_service.set_db(db)
        
        widgets = await widget_service.get_widgets_by_store(store_id)
        
        return [
            WidgetConfigType(
                id=str(w["_id"]),
                store_id=str(w["store_id"]),
                domain=w["domain"],
                video_url=w["video_url"],
                banner_text=w.get("banner_text", ""),
                is_active=w["is_active"],
                created_at=w["created_at"],
                updated_at=w["updated_at"],
            )
            for w in widgets
        ]
    
    @strawberry.field
    async def get_analytics_summary(
        self,
        store_id: str = strawberry.argument(name="storeId"),
        info=None
    ) -> AnalyticsSummaryType:
        """Get analytics summary for a store (requires auth)"""
        # TODO: Add auth check
        db = mongo_module.db
        widget_service.set_db(db)
        
        summary = await widget_service.get_analytics_summary(store_id)
        
        return AnalyticsSummaryType(
            page_view=summary.get("page_view", 0),
            video_loaded=summary.get("video_loaded", 0),
            link_clicked=summary.get("link_clicked", 0),
        )


@strawberry.type
class WidgetMutation:
    @strawberry.mutation
    async def create_widget(
        self,
        store_id: str,
        domain: str,
        video_url: str,
        banner_text: str = "",
        info=None
    ) -> WidgetConfigType:
        """Create widget configuration (requires auth)"""
        # TODO: Add auth check
        db = mongo_module.db
        widget_service.set_db(db)
        
        widget_id = await widget_service.create_widget(
            store_id=store_id,
            domain=domain,
            video_url=video_url,
            banner_text=banner_text
        )
        
        widget = await widget_service.get_widget_by_id(widget_id)
        
        return WidgetConfigType(
            id=str(widget["_id"]),
            store_id=str(widget["store_id"]),
            domain=widget["domain"],
            video_url=widget["video_url"],
            banner_text=widget.get("banner_text", ""),
            is_active=widget["is_active"],
            created_at=widget["created_at"],
            updated_at=widget["updated_at"],
        )
    
    @strawberry.mutation
    async def update_widget(
        self,
        widget_id: str,
        video_url: Optional[str] = None,
        banner_text: Optional[str] = None,
        is_active: Optional[bool] = None,
        info=None
    ) -> Optional[WidgetConfigType]:
        """Update widget configuration (requires auth)"""
        # TODO: Add auth check
        db = mongo_module.db
        widget_service.set_db(db)
        
        success = await widget_service.update_widget(
            widget_id=widget_id,
            video_url=video_url,
            banner_text=banner_text,
            is_active=is_active
        )
        
        if not success:
            return None
        
        widget = await widget_service.get_widget_by_id(widget_id)
        
        return WidgetConfigType(
            id=str(widget["_id"]),
            store_id=str(widget["store_id"]),
            domain=widget["domain"],
            video_url=widget["video_url"],
            banner_text=widget.get("banner_text", ""),
            is_active=widget["is_active"],
            created_at=widget["created_at"],
            updated_at=widget["updated_at"],
        )
    
    @strawberry.mutation
    async def delete_widget(
        self,
        widget_id: str,
        info=None
    ) -> bool:
        """Delete widget configuration (requires auth)"""
        # TODO: Add auth check
        db = mongo_module.db
        widget_service.set_db(db)
        
        return await widget_service.delete_widget(widget_id)
    
    @strawberry.mutation
    async def track_event(
        self,
        store_id: str,
        domain: str,
        event_type: str,
        user_agent: str = "",
        ip_address: str = "",
        info=None
    ) -> bool:
        """Track analytics event (PUBLIC - no auth required)"""
        db = mongo_module.db
        widget_service.set_db(db)
        
        try:
            await widget_service.track_event(
                store_id=store_id,
                domain=domain,
                event_type=event_type,
                user_agent=user_agent,
                ip_address=ip_address
            )
            return True
        except Exception as e:
            print(f"Error tracking event: {e}")
            return False
