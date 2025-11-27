import strawberry
from typing import Optional
import db.mongo as mongo_module
from services.auth import auth_service


@strawberry.type
class User:
    id: str
    username: str
    display_name: str


@strawberry.type
class AuthResponse:
    success: bool
    message: str
    user_id: Optional[str] = None
    username: Optional[str] = None
    display_name: Optional[str] = None
    access_token: Optional[str] = None


@strawberry.type
class Query:
    @strawberry.field
    async def hello(self) -> str:
        return "Hello from GraphQL!"


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def register(
        self,
        username: str,
        password: str,
        display_name: str
    ) -> AuthResponse:
        db = mongo_module.db
        auth_service.set_db(db)
        
        success, result, user_data = await auth_service.register(
            username=username,
            password=password,
            display_name=display_name
        )
        
        if not success:
            return AuthResponse(
                success=False,
                message=result
            )
        
        return AuthResponse(
            success=True,
            message="Registration successful",
            user_id=user_data["user_id"],
            username=user_data["username"],
            display_name=user_data["display_name"],
            access_token=user_data["access_token"]
        )
    
    @strawberry.mutation
    async def login(
        self,
        username: str,
        password: str
    ) -> AuthResponse:
        db = mongo_module.db
        auth_service.set_db(db)
        
        success, result, user_data = await auth_service.login(
            username=username,
            password=password
        )
        
        if not success:
            return AuthResponse(
                success=False,
                message=result
            )
        
        return AuthResponse(
            success=True,
            message="Login successful",
            user_id=user_data["user_id"],
            username=user_data["username"],
            display_name=user_data["display_name"],
            access_token=user_data["access_token"]
        )


user_schema = strawberry.Schema(query=Query, mutation=Mutation)
