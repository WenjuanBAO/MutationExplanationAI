"""
公共数据库客户端模块
负责与公共数据库进行交互（API调用、网页抓取等）
"""
from typing import List, Dict, Optional
import httpx
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config.database_manager import PublicDatabase


class PublicDatabaseClient:
    """公共数据库客户端"""
    
    def __init__(self):
        """初始化公共数据库客户端"""
        self.http_client = httpx.AsyncClient(timeout=30.0)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
    
    async def search_pubmed(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        搜索PubMed数据库
        
        Args:
            query: 查询问题
            max_results: 最大结果数
            
        Returns:
            搜索结果列表
        """
        try:
            # PubMed API搜索
            search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            params = {
                "db": "pubmed",
                "term": query,
                "retmax": max_results,
                "retmode": "json"
            }
            
            response = await self.http_client.get(search_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # 获取摘要信息
            if "esearchresult" in data and "idlist" in data["esearchresult"]:
                pmids = data["esearchresult"]["idlist"]
                return await self._fetch_pubmed_summaries(pmids)
            
            return []
        except Exception as e:
            return [{"error": f"PubMed搜索失败: {str(e)}"}]
    
    async def _fetch_pubmed_summaries(self, pmids: List[str]) -> List[Dict]:
        """获取PubMed摘要信息"""
        try:
            fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
            params = {
                "db": "pubmed",
                "id": ",".join(pmids),
                "retmode": "xml"
            }
            
            response = await self.http_client.get(fetch_url, params=params)
            response.raise_for_status()
            
            # 这里应该解析XML，简化处理
            return [
                {
                    "pmid": pmid,
                    "content": "PubMed摘要内容（需要XML解析）",
                    "source": "PubMed"
                }
                for pmid in pmids
            ]
        except Exception as e:
            return [{"error": f"获取摘要失败: {str(e)}"}]
    
    async def search_uniprot(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        搜索UniProt数据库
        
        Args:
            query: 查询问题
            max_results: 最大结果数
            
        Returns:
            搜索结果列表
        """
        try:
            search_url = "https://rest.uniprot.org/uniprotkb/search"
            params = {
                "query": query,
                "format": "json",
                "size": max_results
            }
            
            response = await self.http_client.get(search_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            results = []
            if "results" in data:
                for item in data["results"]:
                    results.append({
                        "accession": item.get("primaryAccession", ""),
                        "name": item.get("uniProtkbId", ""),
                        "content": item.get("description", ""),
                        "source": "UniProt"
                    })
            
            return results
        except Exception as e:
            return [{"error": f"UniProt搜索失败: {str(e)}"}]
    
    async def search_public_database(
        self, 
        db_config: PublicDatabase, 
        query: str, 
        max_results: int = 10
    ) -> List[Dict]:
        """
        根据配置搜索公共数据库
        
        Args:
            db_config: 公共数据库配置
            query: 查询问题
            max_results: 最大结果数
            
        Returns:
            搜索结果列表
        """
        db_name = db_config.name.lower()
        
        if "pubmed" in db_name:
            return await self.search_pubmed(query, max_results)
        elif "uniprot" in db_name:
            return await self.search_uniprot(query, max_results)
        else:
            # 通用API调用
            if db_config.api_endpoint:
                try:
                    response = await self.http_client.get(
                        db_config.api_endpoint,
                        params={"query": query, "limit": max_results}
                    )
                    response.raise_for_status()
                    return [{"content": response.text, "source": db_config.name}]
                except Exception as e:
                    return [{"error": f"API调用失败: {str(e)}"}]
            else:
                return [{"error": f"未实现该数据库的搜索方法: {db_config.name}"}]
    
    async def close(self):
        """关闭HTTP客户端"""
        await self.http_client.aclose()
