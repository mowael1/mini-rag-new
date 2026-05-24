from src.controllers.BaseController import BaseController
import os

class ProjectController(BaseController):
    
    def __init__(self):
        super().__init__()
        
    # الي هتيجليfiles الي هحط فيه ال folder بتاع path دي المسئوله انها تعملي او تجبلي ال 
    def get_project_path(self, project_id: str):
        
        # project_id بتاع ال path هنا انا بس بجيب ال 
        project_dir = os.path.join(
            self.files_dir,
            project_id
        )
        
        # يبقي انشأهfiles ده مش موجود جوه ال project_id وهنا انا بقوله لو ال 
        if not os.path.exists(project_dir):
            os.makedirs(project_dir)
            
        return project_dir