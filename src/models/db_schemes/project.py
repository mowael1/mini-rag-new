# الي عندنا collection او شكل ال  scheme ده الي هيكون فيه ال 
# لانه هو ده الي هو بيفهمه ObjectId المفروض بتبعت نوعه mongo لما تيجي تبعته ل _id وبالنسبه ل 
# عشان تتعامل معاه str بتاخده ك python ولما تيجي تستقبله في ال 

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from bson.objectid import ObjectId

class Project(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    id: Optional[ObjectId] = Field(None,alias="_id")
    project_id: str = Field(..., min_length=1)

    # project_id علي ال validateده انت عاوز تعمل 
    @field_validator("project_id")
    def validate_project_id(cls, value):
        if not value.isalnum():
            raise ValueError("project_id must be alphanumeric")
        return value
    
    # نفسه model والي هنبدا اننا نطبقها في ال indexing فيبقي هي دي الحاجات الي احنا هنعمل عليها 
    @classmethod
    def get_indexs(cls):
        
        return [
            {
                # indexing دي الحاجات الي هنعمل عليها 
                "key": [
                    ("project_id", 1)
                ],
                # indexing ده الاسم الي هيكون بتاع ال 
                "name": "project_id_index_1",
                # ولا لا unique ودي انت بتقوله هل انت هتكون قيمه 
                "unique": True
            }
        ]