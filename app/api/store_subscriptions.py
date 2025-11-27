import strawberry
import asyncio
from typing import AsyncGenerator
import db.mongo as mongo_module
from services.store import store_service
from api.store_schema import Store, Model
from core.config import settings

BackEND_URL = settings.BACKEND_URL

def normalize_image_url(image_url: str) -> str:
    if not image_url:
        return ""
    if image_url.startswith("http"):
        return image_url
    clean_path = image_url.lstrip("./").lstrip("../")
    return f"{BackEND_URL}/{clean_path}"


def normalize_model_url(model_url: str) -> str:
    if not model_url:
        return ""
    if model_url.startswith("http"):
        return model_url
    clean_path = model_url.lstrip("./").lstrip("../").lstrip("/")
    return f"{BackEND_URL}/{clean_path}"


_store_subscriptions = {}


@strawberry.type
class Subscription:
    @strawberry.subscription
    async def store_updated(self, store_id: str) -> AsyncGenerator[Store, None]:
        db = mongo_module.db
        store_service.set_db(db)
        
        if store_id not in _store_subscriptions:
            _store_subscriptions[store_id] = []
        
        sub_id = id(self)
        _store_subscriptions[store_id].append(sub_id)
        
        try:
            s = await store_service.get_store_by_id(store_id)
            if s:
                yield Store(
                    id=s["id"],
                    name=s["name"],
                    description=s.get("description", ""),
                    image_url=normalize_image_url(s.get("image_url", "")),
                    models=[
                        Model(
                            name=m.get("name", ""),
                            glb_url=normalize_model_url(m.get("glb_url", "")),
                            position=m.get("position", [0, 0]),
                            size=m.get("size", [1, 1, 1]),
                            entrance_order=m.get("entrance_order", 0)
                        )
                        for m in s.get("models", [])
                    ],
                    active_user_count=s.get("active_user_count", 0),
                    installed_widget_id=s.get("installed_widget_id"),
                    installed_widget_domain=s.get("installed_widget_domain")
                )
            
            while True:
                await asyncio.sleep(1)
                s = await store_service.get_store_by_id(store_id)
                if s:
                    yield Store(
                        id=s["id"],
                        name=s["name"],
                        description=s.get("description", ""),
                        image_url=normalize_image_url(s.get("image_url", "")),
                        models=[
                            Model(
                                name=m.get("name", ""),
                                glb_url=normalize_model_url(m.get("glb_url", "")),
                                position=m.get("position", [0, 0]),
                                size=m.get("size", [1, 1, 1]),
                                entrance_order=m.get("entrance_order", 0)
                            )
                            for m in s.get("models", [])
                        ],
                        active_user_count=s.get("active_user_count", 0),
                        installed_widget_id=s.get("installed_widget_id"),
                        installed_widget_domain=s.get("installed_widget_domain")
                    )
        finally:
            if store_id in _store_subscriptions:
                _store_subscriptions[store_id] = [
                    s for s in _store_subscriptions[store_id] if s != sub_id
                ]
