from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from bson.objectid import ObjectId

# mongodb بتاعتنا والي هتتخزن في data_chunk بتاعت ال scheme ودي ال 
class DataChunk(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    id: Optional[ObjectId] = Field(None,alias="_id")
    chunk_text: str = Field(..., min_length=1)
    chunk_metadata: object
    chunk_order: int = Field(..., gt=0)
    
    # project.pyالي موجود في _id والي chunk ده هيكون وصله ما بين ال 
    chunk_project_id: ObjectId
    
    chunk_asset_id: ObjectId

        # نفسه model والي هنبدا اننا نطبقها في ال indexing فيبقي هي دي الحاجات الي احنا هنعمل عليها 
    @classmethod
    def get_indexs(cls):
        
        return [
            {
                # indexing دي الحاجات الي هنعمل عليها 
                # وهنعمله تصاعدي
                "key": [
                    ("chunk_project_id", 1)
                ],
                # indexing ده الاسم الي هيكون بتاع ال 
                "name": "chunk_project_id_index_1",
                # ولا لا unique ودي انت بتقوله هل انت هتكون قيمه 
                "unique": False
            }
        ]
