from src.helpers.config import Settings, get_settings
import os
import random
import string


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
        