"""
RAG引擎核心模块
整合向量检索和生成功能
"""
from typing import List, Dict, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
import os
from dotenv import load_dotenv

from src.config.database_manager import DatabaseManager, LocalDatabase, PublicDatabase
from src.rag.vector_store import VectorStoreManager
from src.rag.public_db_client import PublicDatabaseClient

load_dotenv()


class RAGEngine:
    """RAG引擎"""
    
    def __init__(
        self,
        database_manager: DatabaseManager,
        use_local_model: bool = False,
        model_name: str = "gpt-3.5-turbo"
    ):
        """
        初始化RAG引擎
        
        Args:
            database_manager: 数据库管理器
            use_local_model: 是否使用本地模型
            model_name: 模型名称
        """
        self.database_manager = database_manager
        self.vector_store_manager = VectorStoreManager()
        self.public_db_client = PublicDatabaseClient()
        self.use_local_model = use_local_model
        self.model_name = model_name
        
        # 初始化LLM
        if use_local_model:
            # 使用本地模型（需要根据实际情况配置）
            self.llm = None  # 需要配置本地模型
        else:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                try:
                    self.llm = ChatOpenAI(
                        model=model_name,
                        temperature=0.7,
                        api_key=api_key
                    )
                    print(f"LLM初始化成功: {model_name}")
                except Exception as e:
                    print(f"LLM初始化失败: {str(e)}，将仅返回检索结果")
                    self.llm = None
            else:
                print("警告: 未设置OPENAI_API_KEY环境变量，将仅返回检索结果，不生成答案")
                self.llm = None
        
        # 加载所有本地数据库
        self._load_all_local_databases()
    
    def _load_all_local_databases(self):
        """加载所有本地数据库"""
        local_dbs = self.database_manager.get_local_databases()
        for db_config in local_dbs:
            try:
                self.vector_store_manager.load_local_database(db_config)
                print(f"已加载本地数据库: {db_config.name}")
            except Exception as e:
                print(f"加载数据库 {db_config.name} 失败: {str(e)}")
    
    async def query(
        self,
        question: str,
        use_local_db: bool = True,
        use_public_db: bool = True,
        local_db_names: Optional[List[str]] = None,
        public_db_names: Optional[List[str]] = None,
        top_k: int = 5
    ) -> Dict:
        """
        执行RAG查询
        
        Args:
            question: 用户问题
            use_local_db: 是否使用本地数据库
            use_public_db: 是否使用公共数据库
            local_db_names: 指定使用的本地数据库名称列表（None表示使用全部）
            public_db_names: 指定使用的公共数据库名称列表（None表示使用全部）
            top_k: 每个数据库返回的top k结果
            
        Returns:
            包含检索结果和生成答案的字典
        """
        results = {
            "question": question,
            "local_db_results": {},
            "public_db_results": {},
            "answer": ""
        }
        
        # 检索本地数据库
        if use_local_db:
            if local_db_names:
                # 搜索指定的本地数据库
                for db_name in local_db_names:
                    try:
                        results["local_db_results"][db_name] = \
                            await self.vector_store_manager.search_local_database(
                                db_name, question, top_k
                            )
                    except Exception as e:
                        results["local_db_results"][db_name] = [{"error": str(e)}]
            else:
                # 搜索所有本地数据库
                results["local_db_results"] = \
                    await self.vector_store_manager.search_all_local_databases(
                        question, top_k
                    )
        
        # 检索公共数据库
        if use_public_db:
            public_dbs = self.database_manager.get_public_databases()
            if public_db_names:
                public_dbs = [
                    db for db in public_dbs if db.name in public_db_names
                ]
            
            for db_config in public_dbs:
                try:
                    results["public_db_results"][db_config.name] = \
                        await self.public_db_client.search_public_database(
                            db_config, question, top_k
                        )
                except Exception as e:
                    results["public_db_results"][db_config.name] = {
                        "error": str(e)
                    }
        
        # 生成答案
        results["answer"] = await self._generate_answer(question, results)
        
        return results
    
    async def _generate_answer(
        self,
        question: str,
        retrieval_results: Dict
    ) -> str:
        """
        基于检索结果生成答案
        
        Args:
            question: 用户问题
            retrieval_results: 检索结果
            
        Returns:
            生成的答案
        """
        # 构建上下文
        context_parts = []
        
        # 添加本地数据库结果
        for db_name, results in retrieval_results["local_db_results"].items():
            if isinstance(results, list):
                for result in results:
                    if "content" in result:
                        context_parts.append(
                            f"[{db_name}] {result['content']}"
                        )
        
        # 添加公共数据库结果
        for db_name, results in retrieval_results["public_db_results"].items():
            if isinstance(results, list):
                for result in results:
                    if "content" in result:
                        context_parts.append(
                            f"[{db_name}] {result['content']}"
                        )
        
        context = "\n\n".join(context_parts)
        
        # 构建提示词
        prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""基于以下检索到的上下文信息，回答用户的问题。
如果上下文中没有相关信息，请说明无法从提供的资料中找到答案。

上下文信息：
{context}

用户问题：{question}

请提供详细、准确的答案："""
        )
        
        prompt = prompt_template.format(context=context, question=question)
        
        # 生成答案
        if self.llm:
            try:
                from langchain_core.messages import HumanMessage
                messages = [HumanMessage(content=prompt)]
                response = await self.llm.ainvoke(messages)
                if hasattr(response, 'content'):
                    return response.content
                return str(response)
            except Exception as e:
                return f"生成答案时出错: {str(e)}"
        else:
            # 如果没有LLM，返回检索到的内容摘要
            return f"检索到 {len(context_parts)} 条相关信息。请查看检索结果获取详细信息。"
    
    async def close(self):
        """关闭资源"""
        await self.public_db_client.close()
        await self.vector_store_manager.close()
