from pydantic import BaseModel
from typing import Optional

class ProcessRequest(BaseModel):
    
    file_id: str
    chunk_size: Optional[int] = 100
    overlap_size: Optional[int] = 20
    # الي متخزنه قبل كدهchunks فلو هو ب واحد يبقي هيشيل كل ال  action ده هيأدي الي 
    do_reset: Optional[int] = 0