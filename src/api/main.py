"""
FastAPI应用主入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

from src.api.routes import router, initialize_rag_engine

load_dotenv()

app = FastAPI(
    title="MutationExplanationAI RAG API",
    description="基于RAG的突变解释AI系统API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化RAG引擎"""
    config_path = os.getenv("DATABASE_CONFIG_PATH", "config/database_config.yaml")
    use_local_model = os.getenv("USE_LOCAL_MODEL", "false").lower() == "true"
    model_name = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
    
    try:
        initialize_rag_engine(
            config_path=config_path,
            use_local_model=use_local_model,
            model_name=model_name
        )
        print("RAG引擎初始化成功")
    except Exception as e:
        print(f"RAG引擎初始化失败: {str(e)}")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时清理资源"""
    from src.api.routes import rag_engine
    if rag_engine:
        await rag_engine.close()


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(app, host=host, port=port)
