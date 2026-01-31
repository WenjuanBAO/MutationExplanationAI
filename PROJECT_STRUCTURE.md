# 项目结构说明

## 目录结构

```
MutationExplanationAI/
│
├── config/                          # 配置文件目录
│   └── database_config.yaml        # 数据库配置文件（本地和公共数据库）
│
├── src/                            # 源代码目录
│   ├── __init__.py
│   │
│   ├── api/                        # API接口模块
│   │   ├── __init__.py
│   │   ├── main.py                # FastAPI应用主入口
│   │   ├── routes.py              # API路由定义
│   │   └── models.py              # 请求/响应数据模型
│   │
│   ├── config/                    # 配置管理模块
│   │   ├── __init__.py
│   │   └── database_manager.py    # 数据库配置管理器
│   │
│   └── rag/                       # RAG核心功能模块
│       ├── __init__.py
│       ├── rag_engine.py          # RAG引擎（整合检索和生成）
│       ├── vector_store.py        # 本地向量数据库管理
│       └── public_db_client.py    # 公共数据库客户端
│
├── data/                          # 数据目录（本地数据库存储位置）
│
├── main.py                        # 应用启动入口
├── requirements.txt               # Python依赖包列表
├── .env                          # 环境变量配置（需要创建）
├── env.example.txt               # 环境变量示例
├── .gitignore                    # Git忽略文件
├── README.md                     # 项目说明文档
├── USAGE.md                      # 使用指南
├── PROJECT_STRUCTURE.md          # 项目结构说明（本文件）
├── run.bat                       # Windows启动脚本
└── run.sh                        # Linux/Mac启动脚本
```

## 模块说明

### 1. API模块 (`src/api/`)

负责提供HTTP API接口，接收前端请求并返回结果。

- **main.py**: FastAPI应用初始化、中间件配置、启动事件
- **routes.py**: 定义所有API端点（/query, /databases, /health等）
- **models.py**: 定义请求和响应的数据模型（Pydantic）

### 2. 配置管理模块 (`src/config/`)

负责加载和管理数据库配置信息。

- **database_manager.py**: 
  - 从YAML文件加载数据库配置
  - 提供数据库查询接口
  - 管理本地数据库和公共数据库配置

### 3. RAG核心模块 (`src/rag/`)

实现RAG的核心功能。

- **rag_engine.py**: 
  - 整合向量检索和生成功能
  - 协调本地数据库和公共数据库的查询
  - 调用LLM生成最终答案

- **vector_store.py**: 
  - 管理本地向量数据库连接
  - 实现向量相似度搜索
  - 支持ChromaDB等向量数据库

- **public_db_client.py**: 
  - 实现公共数据库的API调用
  - 支持PubMed、UniProt等公共数据库
  - 处理HTTP请求和响应

## 数据流

```
前端请求
    ↓
API路由 (routes.py)
    ↓
RAG引擎 (rag_engine.py)
    ├──→ 向量存储管理器 (vector_store.py) → 本地数据库
    └──→ 公共数据库客户端 (public_db_client.py) → 公共数据库API
    ↓
整合检索结果
    ↓
LLM生成答案
    ↓
返回给前端
```

## 配置文件说明

### database_config.yaml

定义所有数据库的连接信息：

- **local_databases**: 本地数据库列表
  - name: 数据库名称
  - type: 数据库类型（chroma, faiss等）
  - path: 数据库文件路径
  - description: 数据库描述

- **public_databases**: 公共数据库列表
  - name: 数据库名称
  - type: 数据库类型
  - official_url: 官方访问链接
  - api_endpoint: API端点
  - description: 数据库描述
  - access_method: 访问方式（api, web_scraping等）

### .env

环境变量配置：

- OPENAI_API_KEY: OpenAI API密钥
- HOST: 服务器地址
- PORT: 服务器端口
- DATABASE_CONFIG_PATH: 数据库配置文件路径
- USE_LOCAL_MODEL: 是否使用本地模型
- MODEL_NAME: 使用的模型名称

## 扩展指南

### 添加新的本地数据库类型

1. 在 `src/rag/vector_store.py` 的 `load_local_database` 方法中添加新类型支持
2. 实现对应的加载和搜索逻辑

### 添加新的公共数据库

1. 在 `src/rag/public_db_client.py` 中添加新的搜索方法
2. 在 `search_public_database` 方法中添加路由逻辑
3. 在 `config/database_config.yaml` 中添加配置

### 更换LLM模型

1. 修改 `src/rag/rag_engine.py` 中的LLM初始化代码
2. 更新 `.env` 文件中的相关配置
