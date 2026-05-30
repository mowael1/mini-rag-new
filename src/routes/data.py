from fastapi import APIRouter, UploadFile, Depends, status, Request
from fastapi.responses import JSONResponse
from src.helpers.config import Settings , get_settings
from src.controllers.DataController import DataController
from src.controllers.ProcessController import ProcessController
import aiofiles
from src.models.enums.ResponseEnum import ResponseSignal
import logging
from src.routes.schemas.data import ProcessRequest
from src.models.ProjectModel import ProjectModel
from src.models.ChunkModel import ChunkModel
from src.models.db_schemes.data_chunk import DataChunk

from src.models.AssetModel import AssetModel
from src.models.db_schemes.asset import Asset
from src.models.enums.AssetTypeEnum import AssetTypeEnum
import os

logger = logging.getLogger("uvicorn.error")

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"]
)

# deskالي هترفعه وتبدا انها تخرنه علي ال file دي المسئوله عن انها تستقبل ال 
@data_router.post("/upload/{project_id}")
async def upload_data(request: Request, project_id: str, file: UploadFile, app_settings: Settings= Depends(get_settings)):
    
    #========================================================#
    # mongo في ال projectدي الخاصه بانها تضفلي ال 
    # project_model = ProjectModel(db_client=request.app.db_client)
    
    # indexing هنا احنا عدلنا الي فوق عشان نبدا اننا نضيف ال 
    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    
    project = await project_model.get_project_or_create_one(project_id=project_id)
    #========================================================#
    
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
        
        
    #======================================================#
    #store the assets into the database
    
    asset_model = await AssetModel.create_instance(db_client=request.app.db_client)
    
    asset_resource = Asset(
        asset_project_id = project.id,
        asset_type= AssetTypeEnum.FILE.value,
        asset_name = file_id,
        asset_size = os.path.getsize(file_path)
    )
    
    asset_record = await asset_model.create_asset(asset= asset_resource)
    #======================================================#
    
    return JSONResponse(
        content={
            "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
            "file_id_in_assets": str(asset_record.id),
            "project_id": str(project.id)
        }
    )
    
    
# chunks الي file دي المسئوله انها تقطع ال 
# هيتبعتله JSON في ملف data وباقي ال file_idوده الي هياخد ال 
# ProcessRequest الي بيتجي دي بتكون موجوده في data وشكل ال 
# process_request وانا بستقبلها في ال 
@data_router.post("/process/{project_id}")
async def process_endpoint(request: Request, project_id: str, process_request: ProcessRequest):

    # file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset
    #========================================================#
    # mongo في ال projectدي الخاصه بانها تضفلي ال 
    # project_model = ProjectModel(db_client=request.app.db_client)
    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    
    project = await project_model.get_project_or_create_one(project_id=project_id)
    
    #========================================================#
    
    #========================================================#
    # Use add assets option
    
    # الي موجووده عندنا file_id دي الي هنحط فيها كل ال 
    project_files_ids = {}

    asset_model = await AssetModel.create_instance(db_client=request.app.db_client)

    # فعلا file_id بعت user دي عشان لو ال 
    if process_request.file_id:
        asset_record = await asset_model.get_asset_record(
            asset_project_id=project.id,
            asset_name=process_request.file_id
        )
        
        if asset_record is None: 
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "singal": ResponseSignal.FILE_ID_ERROR.value
                }
            )
        project_files_ids= {
            asset_record.id: asset_record.asset_name
        }
        
    # assets دي عشان لو هو مبعتش يبقي اروح اجيب الي موجودين في ال 
    else:        
        # mongo موجود في ال record دي كده هو هيرجع كل 
        project_files = await asset_model.get_all_project_assets(
            asset_project_id=project.id,
            asset_type= AssetTypeEnum.FILE.value)
        
        # file_id والي هو بنحطه مكان ال asset_name عشان اجيب بس ال loop وبعد كده هعمل عليه 
        project_files_ids= {
            record.id: record.asset_name
            for record in project_files
        }
        
        if project_files_ids == 0:
            
            return JSONResponse(
            status_code= status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.NO_FILES_ERROR.value}
    )
    #========================================================#
        
    no_records = 0
    no_files = 0
    
    # indexing غيرناها لكده عشان نعمل 
    chunk_model = await ChunkModel.create_instance(db_client=request.app.db_client)
    # for loop دي لازم اشيك عليها الاول قبل ما ادخل علي 
    if do_reset == 1:
        _ = await chunk_model.delete_chunks_by_project_id(project_id=project.id)
        
    for asset_id, file_id in project_files_ids.items():
        
        file_content = ProcessController(project_id=project_id).get_file_content(file_id = file_id)
        
        if file_content is None:
            logger.error(f"Error while processing file: {file_id}")
            continue
        
        
        file_chunks = ProcessController(project_id=project_id).process_file_content(
            file_id= file_id,
            chunk_size=chunk_size,
            overlap_size=overlap_size
        )

        if file_chunks is None or len(file_chunks) == 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "singal": ResponseSignal.PROCESSING_FAILED.value
                }
            )

        file_chunks_records = [
            DataChunk(
                chunk_text= chunk.page_content,
                chunk_metadata= chunk.metadata,
                chunk_order= i+1,
                chunk_project_id=project.id,
                chunk_asset_id= asset_id
            )
            for i, chunk in enumerate(file_chunks)
        ]
        
        #========================================================#            
        no_records += await chunk_model.insert_many_chunks(file_chunks_records)
        no_files += 1
        
    return JSONResponse(
        content={
            "signal": ResponseSignal.PROCESSING_SUCCESS.value,
            "inserted_chunks": no_records,
            "processed_files":no_files
        }
    )
    #========================================================#