"""
API路由定义
"""
from fastapi import APIRouter, HTTPException
from typing import Optional

from src.api.models import QueryRequest, QueryResponse, DatabaseListResponse
from src.config.database_manager import DatabaseManager
from src.rag.rag_engine import RAGEngine

# 全局实例（在实际应用中应该使用依赖注入）
db_manager: Optional[DatabaseManager] = None
rag_engine: Optional[RAGEngine] = None

router = APIRouter()


def initialize_rag_engine(
    config_path: str = "config/database_config.yaml",
    use_local_model: bool = False,
    model_name: str = "gpt-3.5-turbo"
):
    """初始化RAG引擎"""
    global db_manager, rag_engine
    
    db_manager = DatabaseManager(config_path)
    rag_engine = RAGEngine(
        db_manager,
        use_local_model=use_local_model,
        model_name=model_name
    )


@router.get("/", tags=["健康检查"])
async def root():
    """根路径，健康检查"""
    return {"message": "MutationExplanationAI RAG API", "status": "running"}


@router.get("/databases", response_model=DatabaseListResponse, tags=["数据库"])
async def list_databases():
    """获取所有可用数据库列表"""
    if not db_manager:
        raise HTTPException(status_code=500, detail="数据库管理器未初始化")
    
    databases = db_manager.list_all_databases()
    return DatabaseListResponse(
        local_databases=databases["local"],
        public_databases=databases["public"]
    )


@router.post("/query", response_model=QueryResponse, tags=["查询"])
async def query(request: QueryRequest):
    """
    执行RAG查询
    
    - **question**: 用户问题
    - **use_local_db**: 是否使用本地数据库
    - **use_public_db**: 是否使用公共数据库
    - **local_db_names**: 指定使用的本地数据库名称列表
    - **public_db_names**: 指定使用的公共数据库名称列表
    - **top_k**: 每个数据库返回的top k结果
    """
    if not rag_engine:
        raise HTTPException(status_code=500, detail="RAG引擎未初始化")
    
    try:
        result = await rag_engine.query(
            question=request.question,
            use_local_db=request.use_local_db,
            use_public_db=request.use_public_db,
            local_db_names=request.local_db_names,
            public_db_names=request.public_db_names,
            top_k=request.top_k
        )
        
        return QueryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.get("/health", tags=["健康检查"])
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "db_manager_initialized": db_manager is not None,
        "rag_engine_initialized": rag_engine is not None
    }
