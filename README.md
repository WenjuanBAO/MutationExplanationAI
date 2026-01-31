# MutationExplanationAI

基于RAG（检索增强生成）的突变解释AI系统

## 项目简介

本项目实现了一个RAG系统，能够根据前端接收的问题，对本地数据库和公共数据库进行检索，并生成相应的答案。

## 功能特性

1. **本地数据库RAG**：支持对本地向量数据库（如ChromaDB）进行检索
2. **公共数据库RAG**：支持通过API访问公共数据库（如PubMed、UniProt等）
3. **灵活的数据库配置**：通过YAML配置文件管理所有数据库连接信息
4. **RESTful API**：提供标准的HTTP API接口供前端调用

## 项目结构

```
MutationExplanationAI/
├── config/                 # 配置文件目录
│   └── database_config.yaml    # 数据库配置文件
├── src/                    # 源代码目录
│   ├── api/               # API接口模块
│   │   ├── main.py        # FastAPI应用入口
│   │   ├── routes.py      # 路由定义
│   │   └── models.py      # 请求/响应模型
│   ├── config/            # 配置管理模块
│   │   └── database_manager.py  # 数据库配置管理器
│   └── rag/               # RAG核心功能模块
│       ├── rag_engine.py      # RAG引擎
│       ├── vector_store.py    # 向量存储管理
│       └── public_db_client.py # 公共数据库客户端
├── data/                  # 数据目录（本地数据库存储）
├── main.py                # 应用启动入口
├── requirements.txt       # Python依赖
├── .env.example          # 环境变量示例
└── README.md             # 项目说明文档
```

## 快速开始

### 1. 环境要求

- Python 3.8+
- pip

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env` 并填写相关配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，设置必要的环境变量（如OpenAI API Key等）。

### 4. 配置数据库

编辑 `config/database_config.yaml` 文件，配置本地数据库和公共数据库：

- **本地数据库**：指定数据库名称、类型和访问路径
- **公共数据库**：指定数据库名称、官方链接和API端点

### 5. 准备本地数据库

确保本地向量数据库已创建并包含数据。如果使用ChromaDB，数据库应位于配置文件中指定的路径。

### 6. 启动服务

```bash
python main.py
```

服务将在 `http://localhost:8000` 启动。

### 7. 访问API文档

启动服务后，访问以下地址查看API文档：

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API使用示例

### 查询接口

```bash
POST /query
Content-Type: application/json

{
  "question": "什么是BRCA1基因突变？",
  "use_local_db": true,
  "use_public_db": true,
  "top_k": 5
}
```

### 获取数据库列表

```bash
GET /databases
```

## 配置说明

### 数据库配置文件 (database_config.yaml)

#### 本地数据库配置

**HTTP API方式（推荐）：**
```yaml
local_databases:
  - name: "标记位点SNVs"
    type: "http_api"
    base_url: "http://58.211.191.32:9090/basicspace/workflow/workflowHistory/"
    database_id: "68ad766a935353004b524e1c"
    token: "your_access_token_here"
    description: "标记位点SNVs数据库"
```

**文件系统方式：**
```yaml
local_databases:
  - name: "本地知识库1"
    type: "chroma"
    path: "./data/local_db_1"
    description: "本地数据库描述（文件系统方式）"
```

#### 公共数据库配置

```yaml
public_databases:
  - name: "PubMed"
    type: "api"
    official_url: "https://pubmed.ncbi.nlm.nih.gov/"
    api_endpoint: "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    description: "PubMed医学文献数据库"
    access_method: "api"
```

## 开发说明

### 添加新的公共数据库支持

1. 在 `src/rag/public_db_client.py` 中添加新的搜索方法
2. 在 `search_public_database` 方法中添加对应的处理逻辑
3. 在 `config/database_config.yaml` 中添加数据库配置

### 添加新的本地数据库类型

1. 在 `src/rag/vector_store.py` 中添加新的数据库类型支持
2. 实现对应的加载和搜索方法

## 技术栈

- **FastAPI**: Web框架
- **LangChain**: RAG框架
- **ChromaDB**: 向量数据库
- **Sentence Transformers**: 文本嵌入模型
- **OpenAI API**: LLM生成（可选，可替换为本地模型）

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！