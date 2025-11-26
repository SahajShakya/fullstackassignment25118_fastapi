"""Authentication service with JWT and bcrypt"""
from datetime import datetime, timedelta
from typing import Tuple, Optional, Dict, Any

from fastapi import HTTPException
from bson.objectid import ObjectId
from passlib.context import CryptContext
from jose import JWTError, jwt
from core.config import settings


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    
    def __init__(self):
        self.db = None
    
    def set_db(self, db):
        self.db = db
    
    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_token(self, user_id: str, username: str, expires_delta: Optional[timedelta] = None) -> str:
        if expires_delta is None:
            expires_delta = timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
        
        expire = datetime.utcnow() + expires_delta
        to_encode = {
            "user_id": user_id,
            "username": username,
            "exp": expire
        }
        
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    async def register(
        self,
        username: str,
        password: str,
        display_name: str
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        existing_user = await self.db.users.find_one({"username": username})
        if existing_user:
            return False, "Username already exists", None
        
        hashed_password = self.hash_password(password)
        
        
        user_doc = {
            "username": username,
            "password": hashed_password,
            "display_name": display_name,
            "created_at": datetime.utcnow(),
            "last_login": None,
            "active": True
        }
        
        result = await self.db.users.insert_one(user_doc)
        user_id = str(result.inserted_id)
        

        token = self.create_token(user_id, username)
        
        return True, "User registered successfully", {
            "user_id": user_id,
            "username": username,
            "display_name": display_name,
            "access_token": token
        }
    
    async def login(
        self,
        username: str,
        password: str
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
      
        user = await self.db.users.find_one({"username": username})
        if not user:
            return False, "Invalid username or password", None
        
        if not self.verify_password(password, user["password"]):
            return False, "Invalid username or password", None
        
        await self.db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {"last_login": datetime.utcnow()}}
        )
        
        user_id = str(user["_id"])
        token = self.create_token(user_id, username)
        
        return True, "Login successful", {
            "user_id": user_id,
            "username": username,
            "display_name": user.get("display_name", username),
            "access_token": token
        }
    
    
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError:
            return None

    


auth_service = AuthService()
