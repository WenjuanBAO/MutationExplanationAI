"""
API请求和响应模型
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class QueryRequest(BaseModel):
    """查询请求模型"""
    question: str = Field(..., description="用户问题")
    use_local_db: bool = Field(True, description="是否使用本地数据库")
    use_public_db: bool = Field(True, description="是否使用公共数据库")
    local_db_names: Optional[List[str]] = Field(
        None, 
        description="指定使用的本地数据库名称列表（None表示使用全部）"
    )
    public_db_names: Optional[List[str]] = Field(
        None,
        description="指定使用的公共数据库名称列表（None表示使用全部）"
    )
    top_k: int = Field(5, description="每个数据库返回的top k结果", ge=1, le=20)


class QueryResponse(BaseModel):
    """查询响应模型"""
    question: str = Field(..., description="用户问题")
    local_db_results: dict = Field(default_factory=dict, description="本地数据库检索结果")
    public_db_results: dict = Field(default_factory=dict, description="公共数据库检索结果")
    answer: str = Field(..., description="生成的答案")


class DatabaseListResponse(BaseModel):
    """数据库列表响应模型"""
    local_databases: List[str] = Field(..., description="本地数据库列表")
    public_databases: List[str] = Field(..., description="公共数据库列表")
