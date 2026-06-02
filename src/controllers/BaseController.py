from src.helpers.config import Settings, get_settings
import os

class BaseController:
    
    def __init__(self):
        
        self.app_settings = get_settings()
        
        # زي كده src بتاع ال folder ده كده هيرجعلي لحد ال 
        # D:\Programming\mini-rag\mini-rag-new\src
        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        
        # files بتاع ال folder ده كده انت جبت ال 
        # D:\Programming\mini-rag\mini-rag-new\src\assets\files
        self.files_dir = os.path.join(
            self.base_dir,
            "assets/files"
        )
        
        self.database_dir = os.path.join(
            self.base_dir,
            "assets/database"
        )
        
    def get_database_path(self, db_name: str):
        
        database_path = os.path.join(
            self.database_dir,
            db_name
        )
        
        if not os.path.exists(database_path):
            os.makedirs(database_path)
            
        return database_path