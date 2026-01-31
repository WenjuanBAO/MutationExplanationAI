"""
本地数据库HTTP API客户端模块
负责通过HTTP API访问本地数据库
"""
from typing import List, Dict, Optional
import httpx
from sentence_transformers import SentenceTransformer
import numpy as np

from src.config.database_manager import LocalDatabase


class LocalDatabaseClient:
    """本地数据库HTTP API客户端"""
    
    def __init__(self):
        """初始化本地数据库客户端"""
        self.http_client = httpx.AsyncClient(timeout=30.0)
        # 用于计算相似度的嵌入模型
        self.embedding_model = SentenceTransformer(
            'paraphrase-multilingual-MiniLM-L12-v2'
        )
    
    def _build_url(self, base_url: str, database_id: str, token: str) -> str:
        """
        构建完整的数据库访问URL（根据示例代码格式）
        
        Args:
            base_url: 基础URL（固定前缀）
            database_id: 数据库ID（workflow ID）
            token: 访问令牌
            
        Returns:
            完整的URL
        """
        # 根据示例代码，URL格式为：base_url + "/biobank/v1/workflowlaunchs?token=" + token
        base_url = base_url.rstrip('/')
        return f"{base_url}/biobank/v1/workflowlaunchs?token={token}"
    
    async def search_database(
        self,
        db_config: LocalDatabase,
        query: str,
        k: int = 5
    ) -> List[Dict]:
        """
        通过HTTP API搜索本地数据库（获取所有数据，不限制数量）
        
        Args:
            db_config: 本地数据库配置
            query: 查询问题（用于后续相似度搜索，如果API不支持直接查询）
            k: 返回结果数量（用于相似度排序后的top k）
            
        Returns:
            搜索结果列表
        """
        if not db_config.base_url or not db_config.database_id:
            raise ValueError(f"数据库 {db_config.name} 缺少base_url或database_id配置")
        
        if not db_config.token:
            raise ValueError(f"数据库 {db_config.name} 缺少token配置")
        
        # 构建URL（根据示例代码格式）
        url = self._build_url(db_config.base_url, db_config.database_id, db_config.token)
        
        # 构建请求头
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            # 获取所有数据（分页循环）
            all_items = []
            page = 1
            limit = 100  # 每页获取100条，可以根据实际情况调整
            skip = 0
            
            while True:
                # 构建请求体（根据示例代码格式）
                params = {
                    "filterOption": {
                        "filters": {
                            "workflow": db_config.database_id,
                            "filtersIn": []
                        },
                        "skip": skip,
                        "page": page,
                        "type": "detail",
                        "limit": limit
                    }
                }
                
                # 使用POST请求（根据示例代码）
                response = await self.http_client.post(url, json=params, headers=headers)
                response.raise_for_status()
                
                # 解析响应
                data = response.json()
                
                # 提取结果
                if isinstance(data, dict) and "results" in data:
                    items = data["results"]
                elif isinstance(data, list):
                    items = data
                else:
                    items = []
                
                # 如果没有更多数据，退出循环
                if not items:
                    break
                
                all_items.extend(items)
                
                # 如果返回的数据少于limit，说明已经是最后一页
                if len(items) < limit:
                    break
                
                # 准备下一页
                page += 1
                skip += limit
            
            # 如果没有获取到数据，返回空结果
            if not all_items:
                return []
            
            # 如果提供了查询字符串，进行相似度搜索排序
            if query and query.strip():
                # 使用向量相似度搜索对结果进行排序
                results = await self._rank_by_similarity(all_items, query, k)
            else:
                # 如果没有查询字符串，返回所有数据（限制为k条）
                results = []
                for item in all_items[:k]:
                    results.append(self._format_item(item))
            
            return results
            
        except httpx.HTTPStatusError as e:
            return [{"error": f"HTTP错误 {e.response.status_code}: {str(e)}"}]
        except Exception as e:
            return [{"error": f"搜索失败: {str(e)}"}]
    
    def _format_item(self, item: Dict) -> Dict:
        """
        格式化单个数据项为统一格式
        
        Args:
            item: 原始数据项
            
        Returns:
            格式化后的数据项
        """
        if not isinstance(item, dict):
            return {
                "content": str(item),
                "metadata": {},
                "score": 1.0
            }
        
        # 尝试提取内容字段（根据实际API响应格式调整）
        content = (
            item.get("content") or 
            item.get("text") or 
            item.get("description") or
            item.get("title") or
            str(item)
        )
        
        # 提取元数据（排除内容字段）
        metadata = {
            k: v for k, v in item.items() 
            if k not in ["content", "text", "description", "title"]
        }
        
        return {
            "content": content,
            "metadata": metadata,
            "score": item.get("score", item.get("similarity", 1.0))
        }
    
    async def _rank_by_similarity(
        self,
        items: List[Dict],
        query: str,
        k: int
    ) -> List[Dict]:
        """
        使用向量相似度对结果进行排序
        
        Args:
            items: 所有数据项
            query: 查询字符串
            k: 返回top k结果
            
        Returns:
            排序后的结果列表
        """
        if not items:
            return []
        
        try:
            # 提取所有文本内容
            texts = []
            for item in items:
                formatted = self._format_item(item)
                texts.append(formatted["content"])
            
            if not texts:
                return []
            
            # 计算查询向量
            query_embedding = self.embedding_model.encode(query)
            
            # 计算所有文本的向量
            text_embeddings = self.embedding_model.encode(texts)
            
            # 计算相似度
            similarities = np.dot(text_embeddings, query_embedding) / (
                np.linalg.norm(text_embeddings, axis=1) * np.linalg.norm(query_embedding) + 1e-8
            )
            
            # 获取top k
            top_indices = np.argsort(similarities)[::-1][:k]
            
            results = []
            for idx in top_indices:
                formatted = self._format_item(items[idx])
                formatted["score"] = float(similarities[idx])
                results.append(formatted)
            
            return results
            
        except Exception as e:
            # 如果相似度计算失败，返回前k条数据
            return [self._format_item(item) for item in items[:k]]
    
    async def close(self):
        """关闭HTTP客户端"""
        await self.http_client.aclose()
