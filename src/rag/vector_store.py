"""
向量存储模块
负责管理本地向量数据库的连接和查询
支持文件系统路径和HTTP API两种访问方式
"""
from typing import List, Dict, Optional
from pathlib import Path
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

from src.config.database_manager import LocalDatabase
from src.rag.local_db_client import LocalDatabaseClient


class VectorStoreManager:
    """向量存储管理器"""
    
    def __init__(self, embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        """
        初始化向量存储管理器
        
        Args:
            embedding_model: 嵌入模型名称
        """
        self.embedding_model = embedding_model
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': 'cpu'}
        )
        self.vector_stores: Dict[str, Chroma] = {}  # 文件系统向量数据库
        self.http_clients: Dict[str, LocalDatabaseClient] = {}  # HTTP API客户端
        self.http_databases: Dict[str, LocalDatabase] = {}  # HTTP数据库配置
    
    def load_local_database(self, db_config: LocalDatabase):
        """
        加载本地向量数据库（支持文件系统和HTTP API两种方式）
        
        Args:
            db_config: 本地数据库配置
            
        Returns:
            Chroma向量存储对象（文件系统）或None（HTTP API）
        """
        db_type = db_config.type.lower()
        
        if db_type == "http_api":
            # HTTP API方式，不需要加载，只需要保存配置
            if db_config.name not in self.http_clients:
                self.http_clients[db_config.name] = LocalDatabaseClient()
            self.http_databases[db_config.name] = db_config
            return None
        elif db_type in ["chroma", "faiss"]:
            # 文件系统方式
            if not db_config.path:
                raise ValueError(f"数据库 {db_config.name} 缺少path配置")
            
            db_path = Path(db_config.path)
            
            if not db_path.exists():
                raise FileNotFoundError(f"数据库路径不存在: {db_path}")
            
            if db_type == "chroma":
                vector_store = Chroma(
                    persist_directory=str(db_path),
                    embedding_function=self.embeddings
                )
                self.vector_stores[db_config.name] = vector_store
                return vector_store
            else:
                raise ValueError(f"暂不支持的文件系统数据库类型: {db_config.type}")
        else:
            raise ValueError(f"不支持的数据库类型: {db_config.type}")
    
    async def search_local_database(
        self, 
        db_name: str, 
        query: str, 
        k: int = 5
    ) -> List[Dict]:
        """
        在本地数据库中搜索（支持文件系统和HTTP API两种方式）
        
        Args:
            db_name: 数据库名称
            query: 查询问题
            k: 返回结果数量
            
        Returns:
            搜索结果列表
        """
        # 检查是否是HTTP API数据库
        if db_name in self.http_databases:
            db_config = self.http_databases[db_name]
            client = self.http_clients[db_name]
            return await client.search_database(db_config, query, k)
        
        # 文件系统数据库
        if db_name not in self.vector_stores:
            raise ValueError(f"数据库未加载: {db_name}")
        
        vector_store = self.vector_stores[db_name]
        results = vector_store.similarity_search_with_score(query, k=k)
        
        return [
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": score
            }
            for doc, score in results
        ]
    
    async def search_all_local_databases(
        self, 
        query: str, 
        k: int = 5
    ) -> Dict[str, List[Dict]]:
        """
        在所有已加载的本地数据库中搜索（支持文件系统和HTTP API）
        
        Args:
            query: 查询问题
            k: 每个数据库返回结果数量
            
        Returns:
            按数据库名称组织的搜索结果
        """
        all_results = {}
        
        # 搜索文件系统数据库
        for db_name in self.vector_stores:
            try:
                results = await self.search_local_database(db_name, query, k)
                all_results[db_name] = results
            except Exception as e:
                all_results[db_name] = [{"error": str(e)}]
        
        # 搜索HTTP API数据库
        for db_name in self.http_databases:
            try:
                results = await self.search_local_database(db_name, query, k)
                all_results[db_name] = results
            except Exception as e:
                all_results[db_name] = [{"error": str(e)}]
        
        return all_results
    
    async def close(self):
        """关闭所有HTTP客户端"""
        for client in self.http_clients.values():
            await client.close()
