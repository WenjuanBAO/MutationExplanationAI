"""
API测试脚本
用于测试RAG系统的各个功能
"""
import asyncio
import httpx
import json
from typing import Dict, Any


BASE_URL = "http://localhost:8000"


async def test_health_check():
    """测试健康检查接口"""
    print("\n" + "="*50)
    print("测试1: 健康检查接口")
    print("="*50)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/health")
            print(f"状态码: {response.status_code}")
            print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            return response.status_code == 200
        except Exception as e:
            print(f"错误: {str(e)}")
            return False


async def test_list_databases():
    """测试数据库列表接口"""
    print("\n" + "="*50)
    print("测试2: 获取数据库列表")
    print("="*50)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/databases")
            print(f"状态码: {response.status_code}")
            data = response.json()
            print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            if response.status_code == 200:
                print(f"\n本地数据库数量: {len(data.get('local_databases', []))}")
                print(f"公共数据库数量: {len(data.get('public_databases', []))}")
                return True
            return False
        except Exception as e:
            print(f"错误: {str(e)}")
            return False


async def test_query_local_db():
    """测试本地数据库查询"""
    print("\n" + "="*50)
    print("测试3: 本地数据库查询（仅使用本地数据库）")
    print("="*50)
    
    query_data = {
        "question": "什么是SNV？",
        "use_local_db": True,
        "use_public_db": False,
        "top_k": 3
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            print(f"发送查询: {query_data['question']}")
            response = await client.post(
                f"{BASE_URL}/query",
                json=query_data
            )
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n问题: {data.get('question')}")
                print(f"\n本地数据库结果:")
                for db_name, results in data.get('local_db_results', {}).items():
                    print(f"  [{db_name}]:")
                    if isinstance(results, list):
                        for i, result in enumerate(results[:2], 1):  # 只显示前2个结果
                            if "error" in result:
                                print(f"    错误: {result['error']}")
                            else:
                                content = result.get('content', '')[:100]  # 只显示前100字符
                                score = result.get('score', 'N/A')
                                print(f"    结果 {i} (相似度: {score}): {content}...")
                    else:
                        print(f"    {results}")
                
                print(f"\n生成的答案:")
                answer = data.get('answer', '')
                print(f"  {answer[:200]}..." if len(answer) > 200 else f"  {answer}")
                return True
            else:
                print(f"错误响应: {response.text}")
                return False
        except Exception as e:
            print(f"错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


async def test_query_all_databases():
    """测试所有数据库查询"""
    print("\n" + "="*50)
    print("测试4: 所有数据库查询（本地+公共）")
    print("="*50)
    
    query_data = {
        "question": "基因突变",
        "use_local_db": True,
        "use_public_db": True,
        "top_k": 2
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            print(f"发送查询: {query_data['question']}")
            response = await client.post(
                f"{BASE_URL}/query",
                json=query_data
            )
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n问题: {data.get('question')}")
                
                print(f"\n本地数据库结果数量: {len(data.get('local_db_results', {}))}")
                print(f"公共数据库结果数量: {len(data.get('public_db_results', {}))}")
                
                answer = data.get('answer', '')
                if answer:
                    print(f"\n生成的答案 (前200字符):")
                    print(f"  {answer[:200]}...")
                
                return True
            else:
                print(f"错误响应: {response.text}")
                return False
        except Exception as e:
            print(f"错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


async def test_specific_database():
    """测试指定数据库查询"""
    print("\n" + "="*50)
    print("测试5: 指定数据库查询（仅标记位点SNVs）")
    print("="*50)
    
    query_data = {
        "question": "SNV突变",
        "use_local_db": True,
        "use_public_db": False,
        "local_db_names": ["标记位点SNVs"],
        "top_k": 3
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            print(f"发送查询: {query_data['question']}")
            print(f"指定数据库: {query_data['local_db_names']}")
            response = await client.post(
                f"{BASE_URL}/query",
                json=query_data
            )
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n问题: {data.get('question')}")
                
                # 显示指定数据库的结果
                for db_name in query_data['local_db_names']:
                    results = data.get('local_db_results', {}).get(db_name, [])
                    print(f"\n[{db_name}] 结果:")
                    if isinstance(results, list):
                        for i, result in enumerate(results, 1):
                            if "error" in result:
                                print(f"  错误: {result['error']}")
                            else:
                                content = result.get('content', '')[:150]
                                score = result.get('score', 'N/A')
                                print(f"  结果 {i} (相似度: {score}): {content}...")
                
                answer = data.get('answer', '')
                if answer:
                    print(f"\n生成的答案:")
                    print(f"  {answer[:300]}...")
                
                return True
            else:
                print(f"错误响应: {response.text}")
                return False
        except Exception as e:
            print(f"错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


async def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("开始测试 MutationExplanationAI RAG API")
    print("="*60)
    print(f"测试目标: {BASE_URL}")
    print("\n提示: 请确保API服务已启动 (python main.py)")
    
    results = {}
    
    # 测试1: 健康检查
    results["健康检查"] = await test_health_check()
    await asyncio.sleep(1)
    
    # 测试2: 数据库列表
    results["数据库列表"] = await test_list_databases()
    await asyncio.sleep(1)
    
    # 测试3: 本地数据库查询
    results["本地数据库查询"] = await test_query_local_db()
    await asyncio.sleep(1)
    
    # 测试4: 所有数据库查询
    results["所有数据库查询"] = await test_query_all_databases()
    await asyncio.sleep(1)
    
    # 测试5: 指定数据库查询
    results["指定数据库查询"] = await test_specific_database()
    
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
    print("\n提示: 请先启动API服务:")
    print("  python main.py")
    print("\n然后运行此测试脚本")
    print("  python test_api.py")
    print("\n等待5秒后开始测试...")
    
    try:
        result = asyncio.run(run_all_tests())
        exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        exit(1)
    except Exception as e:
        print(f"\n\n测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)
