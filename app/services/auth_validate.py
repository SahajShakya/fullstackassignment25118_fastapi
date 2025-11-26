# services/auth_utils.py
from fastapi import HTTPException
from datetime import datetime, timedelta
from typing import Optional
from services.auth import auth_service
from bson.objectid import ObjectId
import jwt

ACCESS_TOKEN_EXPIRE_MINUTES = 60

async def validate_or_refresh_access_token(access_token: str, db):

    new_access_token = None

    payload = await auth_service.verify_token(access_token)
    if payload:
        user_id = payload.get("user_id")
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(401, "User not found")
        return user, new_access_token

    
    token_doc = await db.access_tokens.find_one({"token": access_token})
    if not token_doc:
        raise HTTPException(401, "Access token invalid or expired")

    refresh_token_doc = token_doc.get("refresh_token")
    if not refresh_token_doc or refresh_token_doc.get("is_expired", True):
        raise HTTPException(401, "Refresh token invalid or expired")


    user_id = refresh_token_doc["user_id"]
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(401, "User not found")

    new_access_token = auth_service.create_token(str(user["_id"]), user["username"])
   
    await db.access_tokens.insert_one({
        "token": new_access_token,
        "refresh_token_id": refresh_token_doc["_id"],
        "user_id": user["_id"],
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    })

    return user, new_access_token
