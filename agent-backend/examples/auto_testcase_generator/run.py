"""运行脚本 - 快速测试用例生成"""
import asyncio
import sys
from pathlib import Path
import io

# 设置输出编码为 UTF-8（Windows 兼容）
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def setup_python_path():
    """配置Python导入路径，支持直接运行此脚本"""
    # 获取当前文件的目录
    current_dir = Path(__file__).resolve().parent
    # 获取agent-backend目录（向上两级）
    agent_backend_dir = current_dir.parent.parent
    # 将agent-backend目录添加到sys.path
    if str(agent_backend_dir) not in sys.path:
        sys.path.insert(0, str(agent_backend_dir))


# 在导入前配置路径
setup_python_path()

# 现在可以使用绝对导入
from examples.auto_testcase_generator.generator import generator


async def demo_text():
    """示例1：从文本需求生成测试用例"""
    print("\n" + "="*80)
    print("🚀 示例1: 从文本需求生成API测试用例")
    print("="*80 + "\n")
    
    requirement = """
用户登录接口：POST /api/v1/auth/login

功能：用户名密码登录，返回JWT Token（有效期24小时）

参数：
- username: 必填，3-20字符
- password: 必填，6-20字符

业务规则：
- 连续失败5次锁定30分钟
- 密码错误返回剩余尝试次数
"""
    
    print(f"📝 输入需求：\n{requirement}")
    print("\n⏳ 正在生成测试用例...")
    print("💡 提示：使用快速模型，预计需要10-30秒...\n")
    
    try:
        # 添加超时控制（60秒，全部使用快速模型）
        print("🔍 [DEBUG] 开始调用 generator.generate()...")
        result = await asyncio.wait_for(
            generator.generate(requirement, test_type="API", max_iterations=2),
            timeout=60.0
        )
        print("🔍 [DEBUG] generator.generate() 调用完成")
        
        print(f"\n{'='*80}")
        print("✅ 测试用例生成完成")
        print(f"{'='*80}")
        print(f"\n📊 需求分析：\n{result.analysis}")
        print(f"\n📋 测试用例：\n{result.testcases}")
        print(f"\n🔍 审查意见：\n{result.review}")
        print(f"\n🔄 迭代次数：{result.iteration}")
        print("\n" + "="*80 + "\n")
        
    except asyncio.TimeoutError:
        print("\n❌ 错误：AI模型调用超时（60秒）")
        print("\n可能的原因：")
        print("  1. 网络连接问题，无法访问 DeepSeek API")
        print("  2. API Key 无效或过期")
        print("  3. API 服务响应缓慢（即使使用快速模型）")
        print("\n💡 解决方案：")
        print("  1. 检查网络连接，确保可以访问 api.deepseek.com")
        print("  2. 验证 API Key 是否有效（可在 config.py 中查看）")
        print("  3. 尝试在浏览器访问：https://api.deepseek.com")
        print("  4. 检查防火墙或代理设置")
        print("\n" + "="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ 错误：{type(e).__name__}: {str(e)}")
        import traceback
        print("\n完整错误信息：")
        traceback.print_exc()
        print("\n💡 请检查：")
        print("  1. API Key 配置是否正确")
        print("  2. 网络连接是否正常")
        print("  3. DeepSeek API 服务是否可用")
        print("\n" + "="*80 + "\n")


async def demo_swagger():
    """示例2：从Swagger批量生成测试用例"""
    print("\n" + "="*80)
    print("🚀 示例2: 从Swagger文档批量生成API测试用例")
    print("="*80 + "\n")
    
    swagger_url = "https://petstore.swagger.io/v2/swagger.json"
    print(f"📄 Swagger文档：{swagger_url}")
    print("⏳ 开始并行生成...\n")
    
    results = await generator.batch_generate_from_swagger(
        swagger_url=swagger_url,
        max_apis=3,
        test_type="API"
    )
    
    print(f"\n{'='*80}")
    print(f"✅ 并行生成完成，共 {len(results)} 个接口")
    print(f"{'='*80}")
    
    for i, result in enumerate(results, 1):
        if result and hasattr(result, 'iteration'):
            print(f"\n📦 [{i}] 迭代{result.iteration}次")
            print(f"📝 需求：{result.requirement[:100] if hasattr(result, 'requirement') else 'N/A'}...")
    
    print("\n" + "="*80 + "\n")


async def demo_document():
    """示例3：从文档生成测试用例"""
    print("\n" + "="*80)
    print("🚀 示例3: 从文档生成测试用例")
    print("="*80 + "\n")
    print("📄 此功能需要提供文档路径")
    print("💡 使用方式: python run.py document <文档路径>")
    print("\n" + "="*80 + "\n")


async def main():
    """主函数 - 直接运行演示"""
    print("\n" + "="*80)
    print("🤖 AI测试用例自动生成器 - 演示运行")
    print("="*80 + "\n")
    
    # 直接运行文本生成示例
    await demo_text()


if __name__ == "__main__":
    asyncio.run(main())

