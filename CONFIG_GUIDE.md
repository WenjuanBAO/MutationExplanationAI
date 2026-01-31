# 数据库配置指南

## 本地数据库配置

### HTTP API方式（推荐）

适用于通过HTTP API访问的本地数据库，访问链接结构为：`base_url + database_id`

**配置示例：**

```yaml
local_databases:
  - name: "标记位点SNVs"
    type: "http_api"
    base_url: "http://58.211.191.32:9090/basicspace/workflow/workflowHistory/"
    database_id: "68ad766a935353004b524e1c"
    token: "your_access_token_here"
    description: "标记位点SNVs数据库"
```

**配置项说明：**

- `name`: 数据库名称（必填）
- `type`: 必须设置为 `"http_api"`（必填）
- `base_url`: 固定前缀URL，例如 `"http://58.211.191.32:9090/basicspace/workflow/workflowHistory/"`（必填）
- `database_id`: 数据库ID，例如 `"68ad766a935353004b524e1c"`（必填）
- `token`: 访问令牌，用于API认证（必填）
- `description`: 数据库描述（可选）

**完整URL构建：**

系统会自动将 `base_url` 和 `database_id` 拼接成完整URL：
```
http://58.211.191.32:9090/basicspace/workflow/workflowHistory/68ad766a935353004b524e1c
```

**Token使用：**

Token会自动添加到请求头的 `Authorization` 字段中，格式为 `Bearer {token}`。

如果您的API需要其他格式的token（如直接使用token值，或使用其他header字段），可以修改 `src/rag/local_db_client.py` 中的token处理逻辑。

### 文件系统方式

适用于本地文件系统中的向量数据库（如ChromaDB、FAISS等）

**配置示例：**

```yaml
local_databases:
  - name: "本地知识库"
    type: "chroma"
    path: "./data/local_db"
    description: "本地向量数据库（文件系统方式）"
```

**配置项说明：**

- `name`: 数据库名称（必填）
- `type`: 数据库类型，如 `"chroma"`, `"faiss"` 等（必填）
- `path`: 数据库文件路径（必填）
- `description`: 数据库描述（可选）

## 公共数据库配置

**配置示例：**

```yaml
public_databases:
  - name: "PubMed"
    type: "api"
    official_url: "https://pubmed.ncbi.nlm.nih.gov/"
    api_endpoint: "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    description: "PubMed医学文献数据库"
    access_method: "api"
```

## 多数据库配置示例

```yaml
local_databases:
  # HTTP API方式
  - name: "标记位点SNVs"
    type: "http_api"
    base_url: "http://58.211.191.32:9090/basicspace/workflow/workflowHistory/"
    database_id: "68ad766a935353004b524e1c"
    token: "token_for_snvs"
    description: "标记位点SNVs数据库"
  
  - name: "另一个数据库"
    type: "http_api"
    base_url: "http://58.211.191.32:9090/basicspace/workflow/workflowHistory/"
    database_id: "another_database_id"
    token: "token_for_another"
    description: "另一个数据库"
  
  # 文件系统方式
  - name: "本地知识库"
    type: "chroma"
    path: "./data/local_db"
    description: "本地向量数据库"

public_databases:
  - name: "PubMed"
    type: "api"
    official_url: "https://pubmed.ncbi.nlm.nih.gov/"
    api_endpoint: "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    description: "PubMed医学文献数据库"
    access_method: "api"
```

## 注意事项

1. **Token安全**：建议将token存储在环境变量中，而不是直接写在配置文件中。可以通过环境变量替换：
   ```yaml
   token: "${LOCAL_DB_TOKEN}"
   ```
   然后在代码中读取环境变量。

2. **URL格式**：`base_url` 可以包含或不包含尾部斜杠，系统会自动处理。

3. **API请求方式**：系统会先尝试GET请求，如果失败则尝试POST请求。如果您的API有特殊要求，可以修改 `src/rag/local_db_client.py`。

4. **响应格式**：系统支持多种响应格式（字典、列表等），会自动解析并转换为统一格式。如果您的API返回格式特殊，可能需要调整 `local_db_client.py` 中的解析逻辑。
