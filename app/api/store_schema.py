
import strawberry
from typing import List, Optional
from middleware.auth_middleware import authmanager
import db.mongo as mongo_module
from services.store import store_service


def normalize_image_url(image_url: str) -> str:
    if not image_url:
        return ""
    if image_url.startswith("http"):
        return image_url
    clean_path = image_url.lstrip("./").lstrip("../")
    return f"http://localhost:8000/{clean_path}"


def normalize_model_url(model_url: str) -> str:
    if not model_url:
        return ""
    if model_url.startswith("http"):
        return model_url
    clean_path = model_url.lstrip("./").lstrip("../").lstrip("/")
    return f"http://localhost:8000/{clean_path}"

@strawberry.type
class Model:
    name: str
    glb_url: str
    position: List[float]
    size: List[float]
    entrance_order: int


@strawberry.type
class Store:
    id: str
    name: str
    description: str
    image_url: str
    models: List[Model]
    active_user_count: int = 0
    session_id: Optional[str] = None 


@strawberry.type
class Query:
    @strawberry.field
    async def get_all_stores(self) -> List[Store]:
        db = mongo_module.db
        store_service.set_db(db)
        stores = await store_service.get_all_stores()
        return [
            Store(
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
                active_user_count=s.get("active_user_count", 0)
            )
            for s in stores
        ]

    @strawberry.field
    async def get_store_by_id(self, store_id: str) -> Optional[Store]:
        db = mongo_module.db
        store_service.set_db(db)
        s = await store_service.get_store_by_id(store_id)
        if not s:
            return None
        return Store(
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
            active_user_count=s.get("active_user_count", 0)
        )

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def enter_store(self, store_id: str, user_id: str, info) -> Store:
        """User enters a store - creates session if space available (max 2)"""
        db = mongo_module.db
        store_service.set_db(db)
        success, result = await store_service.enter_store(store_id, user_id)
        
        if not success:
            print(f"DEBUG: enterStore failed - {result}")
            raise Exception(result)
        
        session_id = result
        print(f"DEBUG: User {user_id} entered store {store_id} with session {session_id}")
        
        s = await store_service.get_store_by_id(store_id)
        return Store(
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
            session_id=session_id 
        )

    @strawberry.mutation
    async def exit_store(self, store_id: str, session_id: str) -> Store:
        db = mongo_module.db
        store_service.set_db(db)
        
        await store_service.exit_store(store_id, session_id)
        
        s = await store_service.get_store_by_id(store_id)
        if not s:
            raise Exception(f"Store {store_id} not found")
        
        return Store(
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
            active_user_count=s.get("active_user_count", 0)
        )

    @strawberry.mutation
    async def update_model_position(
        self, store_id: str, model_name: str, position: List[float], user_id: str, info
    ) -> Store:
        db = mongo_module.db
        store_service.set_db(db)
        
        print(f"DEBUG: Updating model {model_name} in store {store_id} to position {position} by user {user_id}")
        success, message = await store_service.update_model_position(store_id, model_name, position, user_id)
        print(f"DEBUG: Update result: {success} - {message}")
        
        if not success:
            raise Exception(f"Failed to update position: {message}")
        
        s = await store_service.get_store_by_id(store_id)
        if not s:
            raise Exception(f"Store {store_id} not found after update")
        return Store(
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
            active_user_count=s.get("active_user_count", 0)
        )
