# 测试指南

## 测试步骤

### 1. 配置测试（不启动服务）

测试配置加载和数据库连接：

```bash
python test_config.py
```

这个测试会：
- 检查配置文件是否正确加载
- 测试HTTP API数据库连接
- 验证向量存储管理器初始化

### 2. API服务测试（需要启动服务）

#### 2.1 启动API服务

在一个终端窗口运行：

```bash
python main.py
```

或者：

```bash
# Windows
run.bat

# Linux/Mac
bash run.sh
```

服务将在 `http://localhost:8000` 启动。

#### 2.2 运行API测试

在另一个终端窗口运行：

```bash
python test_api.py
```

这个测试会：
- 测试健康检查接口
- 测试数据库列表接口
- 测试本地数据库查询
- 测试所有数据库查询
- 测试指定数据库查询

### 3. 手动测试

#### 3.1 使用curl

```bash
# 健康检查
curl http://localhost:8000/health

# 获取数据库列表
curl http://localhost:8000/databases

# 执行查询
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "什么是SNV？",
    "use_local_db": true,
    "use_public_db": false,
    "top_k": 3
  }'
```

#### 3.2 使用浏览器

访问以下地址查看API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

#### 3.3 使用Python requests

```python
import requests

# 查询
response = requests.post(
    "http://localhost:8000/query",
    json={
        "question": "什么是SNV？",
        "use_local_db": True,
        "use_public_db": False,
        "local_db_names": ["标记位点SNVs"],
        "top_k": 3
    }
)

print(response.json())
```

## 注意事项

1. **OPENAI_API_KEY**: 如果没有设置，系统会仅返回检索结果，不生成答案。这不会影响测试。

2. **HTTP API数据库**: 确保数据库服务器 `http://58.211.191.32:9090` 可访问，并且token有效。

3. **文件系统数据库**: 如果配置了文件系统数据库（如ChromaDB），确保路径存在且包含数据。

4. **网络连接**: 公共数据库（如PubMed）需要网络连接。

## 常见问题

### Q: 测试失败，提示"RAG引擎未初始化"
A: 确保API服务已启动，并且配置文件路径正确。

### Q: HTTP API数据库连接失败
A: 检查：
- 数据库服务器是否可访问
- Token是否正确
- URL格式是否正确

### Q: 没有生成答案
A: 如果没有设置OPENAI_API_KEY，系统只会返回检索结果。这是正常的。
