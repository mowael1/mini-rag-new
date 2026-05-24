from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from bson.objectid import ObjectId

# mongodb بتاعتنا والي هتتخزن في data_chunk بتاعت ال scheme ودي ال 
class Project(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    _id: Optional[ObjectId] = None
    chunk_text: str = Field(..., min_length=1)
    chunk_metadata: str
    chunk_order: int = Field(..., gt=0)
    
    # project.pyالي موجود في _id والي chunk ده هيكون وصله ما بين ال 
    chunk_project_id: ObjectId

    # project_id علي ال validateده انت عاوز تعمل 
    @field_validator("project_id")
    def validate_project_id(cls, value):
        if not value.isalnum():
            raise ValueError("project_id must be alphanumeric")
        return value