from src.controllers.BaseController import BaseController
from src.controllers.ProjectController import ProjectController
from fastapi import UploadFile
from src.models.enums.ResponseEnum import ResponseSignal
import os
import uuid


class DataController(BaseController):
    
    def __init__(self):
        super().__init__()
        
    # file بتاع ال type علي ال validation تعمل function دقولقتي عاوزين نعمل 
    def validate_uploaded_file(self, file:UploadFile):
        
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value
        
        if file.size > self.app_settings.FILE_MAX_SIZE * 1024 * 1024:
            return False, ResponseSignal.FILE_SIZE_EXCEEDED.value
        
        return True, ResponseSignal.FILE_UPLOAD_SUCCESS.value
        

    def generate_file_path(self, project_id: str, file_name: str):
            
        # project path دي الي هتجبلنا ال 
        project_dir_path = ProjectController().get_project_path(project_id= project_id)
        
        # unique file name ده كده انت عملت 
        original_name = file_name.filename          # → "document.pdf"
        extension = os.path.splitext(original_name)[1]  # → ".pdf"
        random_key = str(uuid.uuid4()).replace("-", "") + extension
        
        
        # chunk by chunk بتاعنا file عاوزين بقي نبدا اننا نخرن ال 
        # desk الي هيتكتب علي ال file وده كده مسار ال 
        file_path = os.path.join(
            project_dir_path,
            random_key
        )
        
        return file_path
