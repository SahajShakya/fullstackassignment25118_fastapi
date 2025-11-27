from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from strawberry.fastapi import GraphQLRouter
from db.mongo import connect_to_mongo, close_mongo_connection, db
from api.schema import combined_schema
import os 

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()


app = FastAPI(
    title="Store Visualization API",
    version="1.0",
    description="Real-time 3D store visualization with user authentication",
    lifespan=lifespan
)

# CORS middleware - specific origins for credentials
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "Authorization"]
)

app.include_router(GraphQLRouter(combined_schema), prefix="/graphql")

# Serve static files (media folder)
media_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "media")
if os.path.exists(media_path):
    app.mount("/media", StaticFiles(directory=media_path), name="media")
else:
    print(f"Warning: Media folder not found at {media_path}")


@app.get("/")
async def root():
    """Welcome endpoint"""
    return {
        "message": "Welcome to Store Visualization API",
        "docs": "http://localhost:8000/docs",
        "graphql": "http://localhost:8000/graphql",
        "version": "1.0"
    }


@app.get("/widget/index.js")
async def get_widget():
    """Serve widget JS file for embedding on external domains"""
    widget_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "widget", "index.js")
    
    if not os.path.exists(widget_path):
        return {"error": "Widget file not found"}
    
    with open(widget_path, 'r') as f:
        content = f.read()
    
    return content
