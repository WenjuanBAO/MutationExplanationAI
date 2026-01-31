"""
数据库配置管理模块
负责加载和管理本地数据库和公共数据库的配置信息
"""
import yaml
from pathlib import Path
from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class LocalDatabase(BaseModel):
    """本地数据库配置模型"""
    name: str = Field(..., description="数据库名称")
    type: str = Field(..., description="数据库类型（chroma, faiss, http_api等）")
    path: Optional[str] = Field(None, description="数据库访问路径（文件系统路径，type为chroma/faiss时使用）")
    base_url: Optional[str] = Field(None, description="HTTP API基础URL（type为http_api时使用）")
    database_id: Optional[str] = Field(None, description="数据库ID（type为http_api时使用）")
    token: Optional[str] = Field(None, description="访问令牌（type为http_api时使用）")
    description: str = Field(default="", description="数据库描述")


class PublicDatabase(BaseModel):
    """公共数据库配置模型"""
    name: str = Field(..., description="数据库名称")
    type: str = Field(..., description="数据库类型")
    official_url: str = Field(..., description="官方访问链接")
    api_endpoint: Optional[str] = Field(None, description="API端点")
    description: str = Field(default="", description="数据库描述")
    access_method: str = Field(default="api", description="访问方式")


class DatabaseConfig(BaseModel):
    """数据库配置总模型"""
    local_databases: List[LocalDatabase] = Field(default_factory=list)
    public_databases: List[PublicDatabase] = Field(default_factory=list)


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, config_path: str = "config/database_config.yaml"):
        """
        初始化数据库管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = Path(config_path)
        self.config: Optional[DatabaseConfig] = None
        self.load_config()
    
    def load_config(self) -> None:
        """加载数据库配置"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        self.config = DatabaseConfig(**config_data)
    
    def get_local_databases(self) -> List[LocalDatabase]:
        """获取所有本地数据库配置"""
        return self.config.local_databases if self.config else []
    
    def get_public_databases(self) -> List[PublicDatabase]:
        """获取所有公共数据库配置"""
        return self.config.public_databases if self.config else []
    
    def get_local_database_by_name(self, name: str) -> Optional[LocalDatabase]:
        """根据名称获取本地数据库配置"""
        for db in self.get_local_databases():
            if db.name == name:
                return db
        return None
    
    def get_public_database_by_name(self, name: str) -> Optional[PublicDatabase]:
        """根据名称获取公共数据库配置"""
        for db in self.get_public_databases():
            if db.name == name:
                return db
        return None
    
    def list_all_databases(self) -> Dict[str, List]:
        """列出所有数据库"""
        return {
            "local": [db.name for db in self.get_local_databases()],
            "public": [db.name for db in self.get_public_databases()]
        }
