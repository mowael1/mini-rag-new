from src.controllers.BaseController import BaseController
from src.controllers.ProjectController import ProjectController
from src.models.enums.ProcessEnum import ProcessEnum
from langchain_community.document_loaders import TextLoader, PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

class ProcessController(BaseController):
    
    def __init__(self, project_id: str):
        super().__init__()
        
        self.project_id = project_id
        
        self.project_path = ProjectController().get_project_path(project_id=project_id)
        
    
    def get_file_extension(self , file_id):
        return os.path.splitext(file_id)[-1]  # → ".pdf"
        
    # بناءا علي نوع الملفloader دي الي هتبجلي ال 
    def get_file_loader(self, file_id: str):
        
        file_ext = self.get_file_extension(file_id=file_id)
        file_path = os.path.join(
            self.project_path,
            file_id
        )
        
        if file_ext == ProcessEnum.TXT.value:
            
            return TextLoader(file_path=file_path)
        
        if file_ext == ProcessEnum.PDF.value:
        
            return PyMuPDFLoader(file_path=file_path)
        
        return None
    
    # content الي هتبجلي ال function دي بقي ال 
    def get_file_content(self, file_id: str):
        
        loader = self.get_file_loader(file_id=file_id)
        
        return loader.load()
    
    
    # page_content , metadataفكل واحد بيكون فيها ال chunks الي content دي المسئوله انها تقطع ال 
    def process_file_content(self, file_id: str,chunk_size: int = 100, overlap_size: int= 20):
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap_size)
        pages = self.get_file_content(file_id=file_id)

        chunks = text_splitter.split_documents(pages)
        
        return chunks