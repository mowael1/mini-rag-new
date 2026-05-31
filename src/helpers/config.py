from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    
    APP_NAME: str
    APP_NAME: str
    APP_VERSION: str
    OPENAI_API_KEY: str
    FILE_ALLOWED_TYPES: list
    FILE_MAX_SIZE: int
    FILE_DEFAULT_CHUNK_SIZE: int
    
    MONGODB_URL: str
    MONGODB_DATABASE:str
    
        # ====================== LLM Config ======================
    GENERATION_BACKEND: str
    EMBEDDING_BACKEND: str

    OPENAI_API_KEY: str
    OPENAI_API_URL: str
    COHERE_API_KEY: str

    GENERATION_MODEL_ID: str
    EMBEDDING_MODEL_ID: str
    EMBEDDING_MODEL_SIZE: int
    
    default_input_max_char: int
    default_generation_max_output_tokens: int
    defult_generation_temperature: float
    # الي فوق دي values ده الملف الي هيجيب منه ال 
    class Config:
        env_file = "src\.env"
        
# من اي حته عاديaccess علطول وهتقدر انك تعمله object كان ممكن تتجنب دي وتعمل 
# بس خلينا ماشيين زيه
def get_settings():
    return Settings()