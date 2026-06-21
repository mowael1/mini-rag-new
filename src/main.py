from fastapi import FastAPI
from src.routes import base,data,nlp
from motor.motor_asyncio import AsyncIOMotorClient
from src.helpers.config import get_settings
from contextlib import asynccontextmanager
from src.stores.llm.LLMProviderFactory import LLMProviderFactory
from src.stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory
from src.stores.llm.templates.template_parser import TemplateParser

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

settings = get_settings()

# دي هي دورت حياه التطبيقfunction ان ال python ده بيعرف ال decorator الي 
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ← startup هنا
    
    # mongodb دول كانوا بتوع ال 
    
    # Mongodb serverده الاتصال الفعلي ب 
    # app.mongo_client = AsyncIOMotorClient(settings.MONGODB_URL)
    # معينه database هنا بقي انت عاوز تتعامل مع 
    # app.db_client = app.mongo_client[settings.MONGODB_DATABASE]
    
    postgres_conn = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_MAIN_DATABASE}"
    
    # database مع ال connection والي مسئول عن engine ده ال 
    app.db_engine = create_async_engine(postgres_conn, echo=True)

    app.db_client = sessionmaker(
    bind=app.db_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
    
    # LLM factory هنا احنا عرفنا ال 
    LLM_provider_factory = LLMProviderFactory(config=settings)
    
    # vectordb factory هنا هنعرف ال 
    vectordb_provider_factory = VectorDBProviderFactory(config=settings,db_client=app.db_client)
    
    # generation client هنضيف ال 
    app.generation_client = LLM_provider_factory.create(settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(settings.GENERATION_MODEL_ID)
    
    # embedding clientهنضيف ال 
    app.embedding_client = LLM_provider_factory.create(settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(settings.EMBEDDING_MODEL_ID,
                                            embedding_size=settings.EMBEDDING_MODEL_SIZE)  
    
    # vectordb clientهنضيف ال 
    app.vectordb_client = vectordb_provider_factory.create(settings.VECTOR_DB_BACKEND)
    # connect بعد كده نعمل 
    await app.vectordb_client.connect()
    
    
    # Template هنبدا بقي اننا نحط ال 
    app.template_parser = TemplateParser(
        language=settings.PRIMARY_LANG,
        default_language=settings.DEFAULT_LANG
    ) 
    yield  # ← التطبيق شغال هنا
    
    # ← shutdown هنا
    # app.mongo_client.close()
    
    app.db_engine.dispose()
    await app.vectordb_client.disconnect()
    

app = FastAPI(lifespan=lifespan)


app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)