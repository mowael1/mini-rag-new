from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from bson.objectid import ObjectId
from datetime import datetime, timezone

class Asset(BaseModel):
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    id: Optional[ObjectId] = Field(None,alias="_id")
    # project_id تبع اي file_id عشان نبقي عارفين ال file_id , project_id دي الي هنربط بيه ما بين ال 
    asset_project_id: ObjectId
    # .txt, .pdf سواء هو file دي غالبا هتكون نوع ال 
    asset_type: str = Field(...,min_length=1)
    
    # file_id ده الي هياخد ال 
    asset_name: str = Field(...,min_length=1)
    # الي اترفع file وده حجم ال 
    asset_size: int = Field(ge=0, default=None)
    asset_config: dict = Field(default=None)
    asset_pushed_at: datetime = Field(
    default_factory=lambda: datetime.now(timezone.utc))
    
    @classmethod
    def get_indexs(cls):
        
        return [
            {
                # indexing دي الحاجات الي هنعمل عليها 
                # وهنعمله تصاعدي
                "key": [
                    ("asset_project_id", 1)
                ],
                # indexing ده الاسم الي هيكون بتاع ال 
                "name": "asset_project_id_index_1",
                # ولا لا unique ودي انت بتقوله هل انت هتكون قيمه 
                "unique": False
            },
            
            # كمان تاني indexing هنا بقي انا هعمل 
            # compound indexing وهيكون 
            {
                "key": [
                    ("asset_project_id", 1),
                    ("asset_name", 1)
                ],
                # indexing ده الاسم الي هيكون بتاع ال 
                "name": "asset_project_id_name_index_1",
                # ولا لا unique ودي انت بتقوله هل انت هتكون قيمه 
                "unique": True
            }
        ]
