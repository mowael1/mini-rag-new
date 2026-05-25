from fastapi import FastAPI
from src.routes import base,data
from motor.motor_asyncio import AsyncIOMotorClient
from src.helpers.config import get_settings
from contextlib import asynccontextmanager

settings = get_settings()

# دي هي دورت حياه التطبيقfunction ان ال python ده بيعرف ال decorator الي 
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ← startup هنا
    app.mongo_client = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongo_client[settings.MONGODB_DATABASE]
    
    yield  # ← التطبيق شغال هنا
    
    # ← shutdown هنا
    app.mongo_client.close()

app = FastAPI(lifespan=lifespan)


app.include_router(base.base_router)
app.include_router(data.data_router)