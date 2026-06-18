from src.models.BaseDataModel import BaseDataModel
from src.models.db_schemes import Project
from src.models.enums.DataBaseEnum import DataBaseEnum
from sqlalchemy import select, func

class ProjectModel(BaseDataModel):
    
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        
        self.db_client = db_client
        
        
    #==========================================================#
    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)        
        return instance
    #==========================================================#
    async def create_project(self, project: Project):
        
        async with self.db_client() as session:
            async with session.begin():
                session.add(project)
            await session.refresh(project)
        return project
    
    # لو موجود ترجعه ولو مش موجود تنشاهproject_id دي وظيفتها انها تشروح تدور علي ال 
    async def get_project_or_create_one(self, project_id: str):
        
        async with self.db_client() as session:
            # 1. نفذ الـ query فعليًا
            result = await session.execute(
                # sql statement ده كده انت بنيت ال 
                # session.execute() وعشان تتنفذ حطيناها جوه ال 
                select(Project).where(Project.project_id == project_id)
            )
            project = result.scalar_one_or_none()

            # 2. لو مش موجود، اعمل واحد جديد
            if project is None:
                project_rec = Project(project_id=project_id)
                project = await self.create_project(project_rec)

            return project
        
    
    # pagination دي طبعا لازم نكون مستعملين فيها ال 
    async def get_all_projects(self, page: int = 1, page_size: int = 10):
        async with self.db_client() as session:
            # حساب عدد الصفحات الكلي
            total_documents_result = await session.execute(
                select(func.count(Project.project_id))
            )
            total_documents = total_documents_result.scalar_one()
            total_pages = (total_documents + page_size - 1) // page_size  # ceiling division

            # جيب الصفحة المطلوبة
            query = select(Project).offset((page - 1) * page_size).limit(page_size)
            result = await session.execute(query)
            projects = result.scalars().all()

            return projects, total_pages