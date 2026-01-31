# 使用指南

## 快速开始

### 1. 环境配置

创建 `.env` 文件（参考 `env.example.txt`）：

```bash
OPENAI_API_KEY=your_api_key_here
HOST=0.0.0.0
PORT=8000
```

### 2. 数据库配置

编辑 `config/database_config.yaml`，配置你的数据库：

#### 本地数据库示例

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
  - name: "基因突变知识库"
    type: "chroma"
    path: "./data/gene_mutation_db"
    description: "包含基因突变相关知识的本地数据库（文件系统方式）"
```

#### 公共数据库示例

```yaml
public_databases:
  - name: "PubMed"
    type: "api"
    official_url: "https://pubmed.ncbi.nlm.nih.gov/"
    api_endpoint: "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    description: "PubMed医学文献数据库"
    access_method: "api"
```

### 3. 启动服务

```bash
python main.py
```

或使用启动脚本：

- Windows: `run.bat`
- Linux/Mac: `bash run.sh`

### 4. 测试API

#### 使用curl

```bash
# 获取数据库列表
curl http://localhost:8000/databases

# 执行查询
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "什么是BRCA1基因突变？",
    "use_local_db": true,
    "use_public_db": true,
    "top_k": 5
  }'
```

#### 使用Python

```python
import requests

# 查询
response = requests.post(
    "http://localhost:8000/query",
    json={
        "question": "什么是BRCA1基因突变？",
        "use_local_db": True,
        "use_public_db": True,
        "top_k": 5
    }
)

result = response.json()
print(result["answer"])
```

## API接口说明

### POST /query

执行RAG查询

**请求体：**
```json
{
  "question": "用户问题",
  "use_local_db": true,
  "use_public_db": true,
  "local_db_names": ["数据库1", "数据库2"],  // 可选，指定使用的本地数据库
  "public_db_names": ["PubMed"],  // 可选，指定使用的公共数据库
  "top_k": 5  // 每个数据库返回的结果数量
}
```

**响应：**
```json
{
  "question": "用户问题",
  "local_db_results": {
    "数据库名称": [
      {
        "content": "检索到的内容",
        "metadata": {},
        "score": 0.95
      }
    ]
  },
  "public_db_results": {
    "PubMed": [
      {
        "content": "检索到的内容",
        "source": "PubMed"
      }
    ]
  },
  "answer": "生成的答案"
}
```

### GET /databases

获取所有可用数据库列表

**响应：**
```json
{
  "local_databases": ["数据库1", "数据库2"],
  "public_databases": ["PubMed", "UniProt"]
}
```

### GET /health

健康检查

**响应：**
```json
{
  "status": "healthy",
  "db_manager_initialized": true,
  "rag_engine_initialized": true
}
```

## 前端集成示例

### JavaScript/TypeScript

```typescript
async function queryRAG(question: string) {
  const response = await fetch('http://localhost:8000/query', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      question: question,
      use_local_db: true,
      use_public_db: true,
      top_k: 5
    })
  });
  
  const result = await response.json();
  return result;
}
```

### React示例

```jsx
import { useState } from 'react';

function RAGQuery() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);

  const handleQuery = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, use_local_db: true, use_public_db: true })
      });
      const result = await response.json();
      setAnswer(result.answer);
    } catch (error) {
      console.error('Query failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input 
        value={question} 
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="输入您的问题"
      />
      <button onClick={handleQuery} disabled={loading}>
        {loading ? '查询中...' : '查询'}
      </button>
      {answer && <div>{answer}</div>}
    </div>
  );
}
```

## 常见问题

### 1. 如何添加新的本地数据库？

在 `config/database_config.yaml` 的 `local_databases` 部分添加新配置，确保数据库路径存在且包含向量数据。

### 2. 如何添加新的公共数据库？

1. 在 `src/rag/public_db_client.py` 中实现搜索方法
2. 在 `config/database_config.yaml` 中添加配置

### 3. 如何更换LLM模型？

修改 `.env` 文件中的 `MODEL_NAME` 参数，或设置 `USE_LOCAL_MODEL=true` 使用本地模型。

### 4. 本地数据库如何创建？

使用LangChain和ChromaDB创建向量数据库：

```python
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 加载文档、分割、创建向量数据库
# 详细步骤请参考LangChain文档
```
