from fastapi import APIRouter, status, Request, FastAPI
from fastapi.responses import JSONResponse
from .schemas.nlp import PushRequest,SearchRequest
from ..models.ProjectModel import ProjectModel
from ..models.ChunkModel import ChunkModel
from ..controllers.NLPController import NLPController
from ..models.enums.ResponseEnum import ResponseSignal

import logging

logger = logging.getLogger("uvicorn.error")

nlp_router = APIRouter(
    prefix="/api/v1/nlp",
    tags=["api_v1","nlp"]
)

# qdrant ويضيفها ل embedding الي متخزنه تبعه ويعملها chunks ويروح يشوف ال project_id ده الي هيكون مسؤول انه ياخد ال 
@nlp_router.post("/index/push/{project_id}")
async def index_project(request: Request, project_id: str, push_request: PushRequest):
    
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )
    project = await project_model.get_project_or_create_one(project_id=project_id)
    
    if not project: 
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": ResponseSignal.PROJECT_NOT_FOUND_ERROR.value}
        )
    
    chunk_model = await ChunkModel.create_instance(db_client=request.app.db_client)
    
    nlp_controller = NLPController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client
    )
    
    # ← امسح الـ collection قبل الـ loop خالص
    if push_request.do_reset:
        nlp_controller.vectordb_client.delete_collection(
            collection_name=nlp_controller.create_collection_name(project_id=project.project_id)
        )
    
    has_records = True
    page_no = 1
    inserted_items_count = 0
    idx = 0
    
    while has_records:
        
        page_chunks = await chunk_model.get_project_chunks(project_id=project.id, page_no=page_no)
        
        if not page_chunks or len(page_chunks) == 0:
            has_records = False
            break
        
        page_no += 1
        
        
        chunk_ids = list(range(idx, idx+len(page_chunks)))
        idx += len(page_chunks)
        
        is_inserted = nlp_controller.index_into_vector_db(
            project=project,
            chunks=page_chunks,
            chunk_ids = chunk_ids,
            do_reset=False  # ← مش محتاجها هنا خالص
        )
        
        if not is_inserted:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"signal": ResponseSignal.INSERT_INTO_VECTORDB_ERROR.value}
            )
        
        inserted_items_count += len(page_chunks)
    
    return JSONResponse(
        content={
            "signal": ResponseSignal.INSERT_INTO_VECTORDB_SUCCESS.value,
            "inserted_items_count": inserted_items_count
        }
    )

@nlp_router.get("/index/info/{project_id}")
async def get_project_index_info(request: Request, project_id: str):
    
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )
    project = await project_model.get_project_or_create_one(project_id=project_id)
    
    if not project: 
        return JSONResponse(
            status_code= status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.PROJECT_NOT_FOUND_ERROR.value
            }
        )
        
    nlp_controller = NLPController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client= request.app.embedding_client
    )
    
    collection_info = nlp_controller.get_vector_db_collection_info(project=project)
    
    return JSONResponse(
        content={
            "signal": ResponseSignal.INSERT_INTO_VECTORDB_SUCCESS.value,
            "collection_info": collection_info.model_dump()
        }
    )
    
@nlp_router.post("/index/search/{project_id}")
async def search_index(request: Request, project_id:str, search_request: SearchRequest):
    
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )
    project = await project_model.get_project_or_create_one(project_id=project_id)
    
    if not project: 
        return JSONResponse(
            status_code= status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.PROJECT_NOT_FOUND_ERROR.value
            }
        )
        
    nlp_controller = NLPController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client= request.app.embedding_client,
        template_parser = request.app.template_parser
    )
    
    results = nlp_controller.search_vector_db_collection(project = project, text=search_request.text,limit=search_request.limit)
    
    if not results:
        JSONResponse(
        content={
            "signal": ResponseSignal.VECTORDB_SEARCH_ERROR.value,
        }
    )
    
    return JSONResponse(
        content={
            "signal": ResponseSignal.VECTORDB_SEARCH_SUCCESS.value,
            "results": [r.model_dump() for r in results]  # ← حول كل ScoredPoint لـ dict
        }
    )
    
@nlp_router.post("/index/answer/{project_id}")
async def search_index(request: Request, project_id:str, search_request: SearchRequest):
    
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )
    project = await project_model.get_project_or_create_one(project_id=project_id)
    
    if not project: 
        return JSONResponse(
            status_code= status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.PROJECT_NOT_FOUND_ERROR.value
            }
        )
        
    nlp_controller = NLPController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client= request.app.embedding_client,
        template_parser = request.app.template_parser
    )
    
    
    answer, full_prompt , chat_history = nlp_controller.amswer_rag_question(
        project= project,
        query = search_request.text
    )
    
    if not answer: 
        return JSONResponse(
            status_code= status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.RAG_ANSWER_ERROR.value
            }
        )

    return JSONResponse(
        content={
            "signal": ResponseSignal.RAG_ANSWER_SUCCESS.value,
            "answer": answer,
            "full_prompt": full_prompt,
            "chat_history": chat_history
        }
    )