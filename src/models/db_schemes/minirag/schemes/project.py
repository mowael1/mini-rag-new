from .minirag_base import SQLAlchemyBase
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Project(SQLAlchemyBase):
    
    # table انك تكتبله اسم ال sqlalchemy اول حاجه بنعملها في ال 
    __tablename__ = "projects"
    
    # columns بعد كده هنبدا اننا نحدد اسماء ال 
    # auto incremental وهيكون primary key هو الي هيكون ال project_id ال 
    # sqlalchemy بتاعه والي بيكون موجود بردو جوه ال data type وكمان لازم تحدد ال 
    
    project_id = Column(type_=Integer, primary_key=True, autoincrement=True)
    
    # جدبد column هنعمل system في ال project ميكونش عارف احنا عندنا كام user وان ال security وعشان ال 
    # user وده الي هظهره ل uuid باستخدام 
    project_uuid = Column(UUID, default= uuid.uudi4, unique= True, nullable=False)
    
    
    # امتي create بيتحط اول مره نحدد هو اتعمله record عاوزين بقي دلوقتي اننا مع كل 
    # لو حصل تعديل اصلا record تاني يحدد الوقت الي حصل فيه تعديل علي ال column و 