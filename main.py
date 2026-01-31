"""
应用入口文件
"""
from src.api.main import app
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        "src.api.main:app",
        host=host,
        port=port,
        reload=True  # 开发模式，自动重载
    )
