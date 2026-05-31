from fastapi import FastAPI
from src.routes import base,data
from motor.motor_asyncio import AsyncIOMotorClient
from src.helpers.config import get_settings
from contextlib import asynccontextmanager
from src.stores.llm.LLMProviderFactory import LLMProviderFactory

settings = get_settings()

# دي هي دورت حياه التطبيقfunction ان ال python ده بيعرف ال decorator الي 
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ← startup هنا
    app.mongo_client = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongo_client[settings.MONGODB_DATABASE]
    
    LLM_provider_factory = LLMProviderFactory(config=settings)
    
    # generation client هنضيف ال 
    app.generation_client = LLM_provider_factory.create(settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(settings.GENERATION_MODEL_ID)
    
    # embedding clientهنضيف ال 
    app.embedding_client = LLM_provider_factory.create(settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(settings.EMBEDDING_MODEL_ID,
                                            embedding_size=settings.EMBEDDING_MODEL_SIZE)  
    yield  # ← التطبيق شغال هنا
    
    # ← shutdown هنا
    app.mongo_client.close()

app = FastAPI(lifespan=lifespan)


app.include_router(base.base_router)
app.include_router(data.data_router)