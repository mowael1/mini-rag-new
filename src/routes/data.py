from fastapi import APIRouter, UploadFile, Depends, status
from fastapi.responses import JSONResponse
from src.helpers.config import Settings , get_settings
from src.controllers.DataController import DataController
import aiofiles
from src.models.enums.ResponseEnum import ResponseSignal
import logging

logger = logging.getLogger("uvicorn.error")

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"]
)

@data_router.get("/upload/{project_id}")
async def upload_data(project_id: str, file: UploadFile, app_settings: Settings= Depends(get_settings)):
    
    # validate the file properties
    # DataController فاحنا هنفصله في حته لوحدها والي هيكون موجود في logic وطلما ده 
    is_valid, result_signal = DataController().validate_uploaded_file(file=file)
    
    #ده response هيرجع ال size ويبقي الجزء ده لو الملف مش من النوع الي احنا محددينه او اكبر في ال 
    if not is_valid:
        return JSONResponse(
            status_code= status.HTTP_400_BAD_REQUEST,
            content={
                "signal": result_signal
            }
        )
        
    # لكن لو كمل هنا يبقي الملف سليم وعاوزين اننا نبدا نخزنه بقي
    # project_id عاوزين بقي اننا نخرن الملف ده في مكان يكون ليه علاقه ب 
    # الي هيجيلنا file وهنخزن فيه ال project_id فولدر هيكون اسمه files الي اسمه folder فاحنا هنعمل جوه ال 
    # controllers لوحدها جوه ال function يبقي هحطه في logic وطلما ده 
    # بتاعه project path جوه ال file ده عشان نستعمله في اننا نخزن ال project pathوبعد كده نروح نجيب ال  
    # random ويكن اسم الملف كمان    
    file_path, file_id = DataController().generate_file_path(project_id=project_id, file_name=file)

    #  chunk by chunk من خلال انها تكون desk علي ال file دي المسئوله انها تبدا تكتب ال 
    try:
        async with aiofiles.open(file_path, "wb") as f:
            while True:
                chunk = await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE)
                if not chunk:
                    break
                await f.write(chunk)
    except Exception as e:
        
        logger.error(f"Error while uploading file: {e}")
        return JSONResponse(
            status_code= status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.FILE_UPLOAD_FAILED.value
            }
        )
    return JSONResponse(
        content={
            "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
            "file_id": file_id
        }
    )