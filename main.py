from fastapi import FastAPI
from pydantic import BaseModel, HttpUrl
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import httpx
import os
from typing import Optional


app = FastAPI()

# MongoDB connection
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://mongodb:27017")
client = AsyncIOMotorClient(MONGODB_URL)
db = client.metadata_db
collection = db.urls

class URLRequest(BaseModel):
    url: HttpUrl

class URLResponse(BaseModel):
    url: str
    headers: Optional[dict] = None
    cookies: Optional[dict] = None
    page_source: Optional[str] = None
    collected_at: Optional[datetime] = None
    status: str
    message: Optional[str] = None

async def collect_metadata(url: str):
    
    try:
        async with httpx.AsyncClient() as client:
            response =  await client.get(url)
            
            metadata = {
                "url": url,
                "headers": dict(response.headers),
                "cookies": {cookie.name: cookie.value for cookie in response.cookies.jar},
                "page_source": response.text,
                "collected_at": datetime.utcnow(),
                "status_code": response.status_code
            }
            
            # Update or insert the metadata
            await collection.update_one(
                {"url": url},
                {"$set": metadata},
                upsert=True
            )
    except Exception as e:
        print(f"Error collecting metadata for {url}: {e}")


@app.post("/collect", response_model=URLResponse)
async def collect_url_metadata(request: URLRequest):
   
    url = str(request.url)
    
    await collect_metadata(url)

    
    return URLResponse(
        url=url,
        status="Url_saved",
        message="Metadata collection started"
    )

@app.get("/metadata", response_model=URLResponse)
async def get_url_metadata(url: str):
    """
    GET endpoint to retrieve metadata for a URL.
    If the URL doesn't exist in the database, it triggers collection and returns a message.
    """
    # Check if URL exists in database
    record = await collection.find_one({"url": url})
    
    if record:
        # Record exists, return the metadata
        return URLResponse(
            url=record.get("url"),
            headers=record.get("headers"),
            cookies=record.get("cookies"),
            page_source=record.get("page_source"),
            collected_at=record.get("collected_at"),
            status="exists",
            message="Metadata retrieved successfully"
        )
    else:
        return URLResponse(
            url=url,
            status="not_found",
            message="Record doesn't exist & request has been logged to collect the metadata, please check later"
        )

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "HTTP Metadata Inventory API",
        "status": "running",
        "endpoints": {
            "POST /collect": "Collect metadata for a URL",
            "GET /metadata?url=<url>": "Retrieve metadata for a URL"
        }
    }

@app.on_event("startup")
async def startup_event():
    """Create indexes on startup"""
    await collection.create_index("url", unique=True)
    print("MongoDB indexes created")

@app.on_event("shutdown")
async def shutdown_event():
    """Close MongoDB connection on shutdown"""
    client.close()
    print("MongoDB connection closed")



