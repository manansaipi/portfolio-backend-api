import os
import httpx
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
import time

router = APIRouter(
    prefix="/api/instagram",
    tags=["Instagram"]
)

# Simple in-memory cache to prevent rate-limiting from Meta
cache = {
    "feed": {"data": None, "timestamp": 0},
    "stats": {"data": None, "timestamp": 0},
    "comments": {}
}
CACHE_TTL = 300 # 5 minutes

class InstagramStatResponse(BaseModel):
    followers_count: int
    follows_count: int
    media_count: int
    name: str
    profile_picture_url: Optional[str] = None

class InstagramMedia(BaseModel):
    id: str
    caption: Optional[str] = ""
    media_type: str
    media_url: str
    permalink: str
    thumbnail_url: Optional[str] = None
    timestamp: str

class InstagramComment(BaseModel):
    id: str
    text: str
    username: str
    timestamp: str

def get_ig_credentials():
    token = os.environ.get("META_ACCESS_TOKEN")
    user_id = os.environ.get("IG_USER_ID")
    if not token or not user_id:
        raise HTTPException(status_code=500, detail="Instagram credentials not configured.")
    return token, user_id

@router.get("/stats", response_model=InstagramStatResponse)
async def get_instagram_stats():
    now = time.time()
    if cache["stats"]["data"] and (now - cache["stats"]["timestamp"] < CACHE_TTL):
        return cache["stats"]["data"]

    token, user_id = get_ig_credentials()
    url = f"https://graph.facebook.com/v19.0/{user_id}"
    params = {
        "fields": "followers_count,follows_count,media_count,name,profile_picture_url",
        "access_token": token
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"Meta API Error: {response.text}")
        
        data = response.json()
        cache["stats"]["data"] = data
        cache["stats"]["timestamp"] = now
        return data

@router.get("/feed", response_model=List[InstagramMedia])
async def get_instagram_feed(limit: int = 9):
    now = time.time()
    if cache["feed"]["data"] and (now - cache["feed"]["timestamp"] < CACHE_TTL):
        # We cache the default request, but return up to the requested limit
        return cache["feed"]["data"][:limit]

    token, user_id = get_ig_credentials()
    url = f"https://graph.facebook.com/v19.0/{user_id}/media"
    params = {
        "fields": "id,caption,media_type,media_url,permalink,thumbnail_url,timestamp",
        "limit": max(limit, 20), # Fetch a bit more to cache
        "access_token": token
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"Meta API Error: {response.text}")
        
        data = response.json().get("data", [])
        cache["feed"]["data"] = data
        cache["feed"]["timestamp"] = now
        return data[:limit]

@router.get("/comments/{media_id}", response_model=List[InstagramComment])
async def get_instagram_comments(media_id: str):
    now = time.time()
    if media_id in cache["comments"] and (now - cache["comments"][media_id]["timestamp"] < CACHE_TTL):
        return cache["comments"][media_id]["data"]

    token, _ = get_ig_credentials()
    url = f"https://graph.facebook.com/v19.0/{media_id}/comments"
    params = {
        "fields": "id,text,username,timestamp",
        "access_token": token
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"Meta API Error: {response.text}")
        
        data = response.json().get("data", [])
        cache["comments"][media_id] = {
            "data": data,
            "timestamp": now
        }
        return data
