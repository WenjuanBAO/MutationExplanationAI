"""
配置和组件测试脚本
测试配置加载、数据库连接等基础功能
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from src.config.database_manager import DatabaseManager
from src.rag.local_db_client import LocalDatabaseClient
from src.rag.vector_store import VectorStoreManager


def test_config_loading():
    """测试配置加载"""
    print("\n" + "="*50)
    print("测试1: 配置加载")
    print("="*50)
    
    try:
        db_manager = DatabaseManager("config/database_config.yaml")
        print("✓ 配置文件加载成功")
        
        local_dbs = db_manager.get_local_databases()
        public_dbs = db_manager.get_public_databases()
        
        print(f"\n本地数据库数量: {len(local_dbs)}")
        for db in local_dbs:
            print(f"  - {db.name} (类型: {db.type})")
            if db.type == "http_api":
                print(f"    URL: {db.base_url}{db.database_id}")
                print(f"    Token: {'已设置' if db.token else '未设置'}")
        
        print(f"\n公共数据库数量: {len(public_dbs)}")
        for db in public_dbs:
            print(f"  - {db.name} (类型: {db.type})")
        
        return True
    except Exception as e:
        print(f"✗ 配置加载失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_http_api_connection():
    """测试HTTP API连接"""
    print("\n" + "="*50)
    print("测试2: HTTP API数据库连接测试")
    print("="*50)
    
    try:
        db_manager = DatabaseManager("config/database_config.yaml")
        local_dbs = db_manager.get_local_databases()
        
        http_dbs = [db for db in local_dbs if db.type == "http_api"]
        
        if not http_dbs:
            print("⚠ 没有配置HTTP API类型的本地数据库")
            return True
        
        client = LocalDatabaseClient()
        
        for db_config in http_dbs:
            print(f"\n测试数据库: {db_config.name}")
            print(f"  URL: {db_config.base_url}{db_config.database_id}")
            
            try:
                # 测试连接（使用简单查询）
                results = await client.search_database(
                    db_config,
                    query="test",
                    k=1
                )
                
                if results and "error" not in results[0]:
                    print(f"  ✓ 连接成功，返回 {len(results)} 条结果")
                elif results and "error" in results[0]:
                    print(f"  ⚠ 连接成功但返回错误: {results[0]['error']}")
                else:
                    print(f"  ⚠ 连接成功但无结果返回")
                    
            except Exception as e:
                print(f"  ✗ 连接失败: {str(e)}")
        
        await client.close()
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_vector_store_manager():
    """测试向量存储管理器"""
    print("\n" + "="*50)
    print("测试3: 向量存储管理器初始化")
    print("="*50)
    
    try:
        manager = VectorStoreManager()
        print("✓ 向量存储管理器初始化成功")
        
        db_manager = DatabaseManager("config/database_config.yaml")
        local_dbs = db_manager.get_local_databases()
        
        print(f"\n尝试加载 {len(local_dbs)} 个本地数据库...")
        for db_config in local_dbs:
            try:
                manager.load_local_database(db_config)
                print(f"  ✓ {db_config.name} 加载成功")
            except Exception as e:
                print(f"  ⚠ {db_config.name} 加载失败: {str(e)}")
        
        return True
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("开始测试配置和组件")
    print("="*60)
    
    results = {}
    
    # 测试1: 配置加载
    results["配置加载"] = test_config_loading()
    
    # 测试2: HTTP API连接
    results["HTTP API连接"] = await test_http_api_connection()
    
    # 测试3: 向量存储管理器
    results["向量存储管理器"] = test_vector_store_manager()
    
    # 打印测试总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    for test_name, passed in results.items():
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{test_name}: {status}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\n总计: {passed}/{total} 测试通过")
    
    return all(results.values())


if __name__ == "__main__":
    try:
        result = asyncio.run(run_all_tests())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
