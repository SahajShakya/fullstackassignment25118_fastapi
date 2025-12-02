# api/decorators/authmanager.py
from app.services.auth_validate import validate_or_refresh_access_token
from fastapi import HTTPException
from functools import wraps
import inspect
import app.db.mongo as mongo_module

def authmanager(resolver):
    @wraps(resolver)
    async def wrapper(*args, **kwargs):
        info = kwargs.get("info")
        if not info:
            raise HTTPException(500, "GraphQL 'info' missing")

        request = info.context.get("request")
        if not request:
            raise HTTPException(500, "Request missing in GraphQL context")

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(401, "Authorization token missing")

        access_token = auth_header.split(" ")[1]

        # Get MongoDB db instance
        db = mongo_module.db
        user, new_access_token = await validate_or_refresh_access_token(access_token, db)

        # Add user info to context
        info.context["user"] = user
        info.context["new_access_token"] = new_access_token

        # Call the resolver
        result = resolver(*args, **kwargs)
        if inspect.iscoroutinefunction(resolver):
            result = await result
        return result

    return wrapper
