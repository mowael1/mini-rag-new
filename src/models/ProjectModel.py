from src.models.BaseDataModel import BaseDataModel
from src.models.db_schemes.project import Project
from src.models.enums.DataBaseEnum import DataBaseEnum

class ProjectModel(BaseDataModel):
    
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        
        self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]
        
        
    #==========================================================#
    # indexing هنا بقي هنبدا اننا نضيف ال 

    # indexes الي هتضيف لينا ال function فاول حاجه احنا عملنا ال 
    # ده collection وهنبقي عاوزين اننا نستدعيها اول ما ننشا ال 
    async def init_collection(self):
        indexes = Project.get_indexs()
        for index in indexes:
            await self.collection.create_index(
                index["key"],
                name=index["name"],
                unique=index["unique"]
            )
            
    # ده collection دي بقي الي انت هتستعملها عشان تعمل ال 
    # فعملنا دي كحاجه وسيطه __init__ مينفعش اننا نضيفها جوه ال async function ودي عملناها لان ال 
    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collection()
        
        return instance
    #==========================================================#
        
    
    # monogdb الي هيجيلك في ال file ده كده انت هتحط ال 
    # await يكون insert وال async تكون function يبقي لازم ال motor وطلما انت بتتعامل مع ال 
    async def create_project(self, project: Project):
        
        # dictionary ده الي project فكان لازم نحول ال dictionary دي هي بتاخد .insert_one ال 
        # dictionary الي pydantic model والي بتحول ال .model_duump() عشان كده استعملنا ال 
        result = await self.collection.insert_one(project.model_dump(by_alias=True, exclude_unset=True))
        project._id = result.inserted_id
        return project
    
    # لو موجود ترجعه ولو مش موجود تنشاهproject_id دي وظيفتها انها تشروح تدور علي ال 
    async def get_project_or_create_one(self, project_id: str):
        
        # dictionary خلي بالك ان دي بترجع 
        record = await self.collection.find_one({
            "project_id": project_id
        })
        
        # ده لو هو ملقهاش
        if record is None:
            #create new project
            project = Project(project_id=project_id)
            project = await self.create_project(project = project)
            
            return project
        
        return Project(**record)
    
    
    # pagination دي طبعا لازم نكون مستعملين فيها ال 
    async def get_all_projects(self, page: int = 1, page_size: int = 10):
        
        total_documents = await self.collection.count_documents({})
        
        skip = (page - 1) * page_size  # ← عدد الـ documents اللي هتتخطاها

        cursor = self.collection.find({}).skip(skip).limit(page_size)
        
        projects = []
        async for project in cursor:
            projects.append(Project(**project))
            
        
        return projects, total_documents