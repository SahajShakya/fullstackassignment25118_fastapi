from datetime import datetime, timedelta
from bson.objectid import ObjectId
from typing import Optional, Dict, Any, List
import uuid

class StoreService:
    def __init__(self):
        self.db = None
    
    def set_db(self, db):
        self.db = db

    
    async def get_all_stores(self) -> List[Dict[str, Any]]:
        stores = await self.db.stores.find({}).to_list(length=None)
        for store in stores:
            store["id"] = str(store["_id"])
            await self._cleanup_stale_sessions(store["_id"])
        return stores


    async def get_store_by_id(self, store_id: str) -> Optional[Dict[str, Any]]:
        await self._cleanup_stale_sessions(ObjectId(store_id))
        
        store = await self.db.stores.find_one({"_id": ObjectId(store_id)})
        if store:
            store["id"] = str(store["_id"])
            # Fetch widget domain if widget is installed
            if store.get("installed_widget_id"):
                widget = await self.db.widget_configs.find_one({
                    "_id": ObjectId(store.get("installed_widget_id"))
                })
                if widget:
                    store["installed_widget_domain"] = widget.get("domain")
        return store


    async def _cleanup_stale_sessions(self, store_id: ObjectId):
        five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
        result = await self.db.stores.update_one(
            {"_id": store_id},
            {
                "$pull": {"active_sessions": {"last_heartbeat": {"$lt": five_minutes_ago}}},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        store = await self.db.stores.find_one({"_id": store_id})
        if store:
            active_sessions = store.get("active_sessions", [])
            unique_users = len(set(str(s["user_id"]) for s in active_sessions))
            
            if unique_users != store.get("active_user_count", 0):
                await self.db.stores.update_one(
                    {"_id": store_id},
                    {"$set": {"active_user_count": unique_users}}
                )


    async def enter_store(self, store_id: str, user_id: str) -> tuple[bool, str]:
    
        await self._cleanup_stale_sessions(ObjectId(store_id))
        
        store = await self.db.stores.find_one({"_id": ObjectId(store_id)})
        if not store:
            return False, "Store not found"
        
        active_sessions = store.get("active_sessions", [])
        
        existing_session = next(
            (s for s in active_sessions if str(s["user_id"]) == str(user_id)),
            None
        )
        if existing_session:
            return True, existing_session["session_id"]
        
        unique_user_ids = set(str(s["user_id"]) for s in active_sessions)
        
        if len(unique_user_ids) >= 2:
            return False, "Store is full - maximum 2 users allowed"
        
        session_id = str(uuid.uuid4())
        new_session = {
            "session_id": session_id,
            "user_id": user_id,
            "entered_at": datetime.utcnow(),
            "last_heartbeat": datetime.utcnow()
        }
        
        await self.db.stores.update_one(
            {"_id": ObjectId(store_id)},
            {
                "$push": {"active_sessions": new_session},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        updated_store = await self.db.stores.find_one({"_id": ObjectId(store_id)})
        if updated_store:
            active_sessions = updated_store.get("active_sessions", [])
            unique_users = len(set(str(s["user_id"]) for s in active_sessions))
            await self.db.stores.update_one(
                {"_id": ObjectId(store_id)},
                {"$set": {"active_user_count": unique_users}}
            )
        
        return True, session_id


    async def exit_store(self, store_id: str, session_id: str) -> bool:
        result = await self.db.stores.update_one(
            {"_id": ObjectId(store_id)},
            {
                "$pull": {"active_sessions": {"session_id": session_id}},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        store = await self.db.stores.find_one({"_id": ObjectId(store_id)})
        if store:
            active_sessions = store.get("active_sessions", [])
            unique_users = len(set(str(s["user_id"]) for s in active_sessions))
            await self.db.stores.update_one(
                {"_id": ObjectId(store_id)},
                {"$set": {"active_user_count": unique_users}}
            )
            print(f"DEBUG: Exit store - removed session {session_id}, remaining unique users: {unique_users}")
        
        return result.modified_count > 0


    async def heartbeat(self, store_id: str, session_id: str) -> bool:
        result = await self.db.stores.update_one(
            {"_id": ObjectId(store_id), "active_sessions.session_id": session_id},
            {
                "$set": {"active_sessions.$.last_heartbeat": datetime.utcnow()}
            }
        )
        return result.modified_count > 0


    async def update_model_position(
        self, store_id: str, model_name: str, new_position: list, user_id: str
    ) -> tuple[bool, str]:
        now = datetime.utcnow()
        
        result = await self.db.stores.update_one(
            {
                "_id": ObjectId(store_id),
                "models.name": model_name
            },
            {
                "$set": {
                    "models.$.position": new_position,
                    "models.$.last_moved_by": user_id,
                    "models.$.last_moved_at": now,
                    "updated_at": now
                }
            }
        )
        
        if result.modified_count > 0:
            return True, "Position updated"
        else:
            return False, "Model not found"


    async def install_widget(self, store_id: str, widget_id: str) -> Optional[Dict[str, Any]]:
        try:
            store_oid = None
            
            if isinstance(store_id, str) and len(store_id) == 24:
                try:
                    store_oid = ObjectId(store_id)
                except:
                    pass
            
            if store_oid is None:
                store = await self.db.stores.find_one({"id": store_id})
                if store:
                    store_oid = store["_id"]
                else:
                    store = await self.db.stores.find_one({})
                    if store:
                        store_oid = store["_id"]
                    else:
                        return None
            
            result = await self.db.stores.update_one(
                {"_id": store_oid},
                {
                    "$set": {
                        "installed_widget_id": widget_id,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                store = await self.db.stores.find_one({"_id": store_oid})
                if store:
                    store["id"] = str(store["_id"])
                return store
            else:
                return None
        except Exception as e:
            print(f"Error installing widget: {e}")
            return None


store_service = StoreService()
