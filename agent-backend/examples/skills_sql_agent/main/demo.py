"""
主程序演示
展示 Skills SQL Agent 的使用
"""

import asyncio
import sys
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

from logic.agent import AgentManager

async def run_demo():
    """运行演示，展示 progressive disclosure 的效果"""
    
    # 设置数据库路径
    base_path = Path(__file__).parent.parent.parent
    db_path = base_path / "data" / "skills_demo.db"
    memory_db_path = base_path / "data" / "skills_memory.db"
    
    # 创建Agent管理器
    agent_manager = AgentManager(db_path, memory_db_path)
    
    # 创建agent
    agent = await agent_manager.create_skills_agent()
    
    print("\n" + "="*60)
    print("🤖 Skills SQL Agent 演示开始")
    print("="*60)
    
    # 演示问题
    question = "Write a SQL query to find all customers who made orders over $1000 in the last month"
    
    print(f"\n👤 用户问题: {question}")
    print("-" * 60)
    
    try:
        print("[处理] 正在调用 AI 助手...")
        
        # 使用异步流式处理
        async for event in agent.astream(
            {"messages": [{"role": "user", "content": question}]},
            stream_mode="updates",
        ):
            for node_name, node_data in event.items():
                if "messages" in node_data:
                    for msg in node_data["messages"]:
                        try:
                            msg.pretty_print()
                        except Exception as e:
                            print(f"[输出] {msg}")
        
        print("\n[成功] AI 助手回复完成!")
                
    except Exception as e:
        print(f"[错误] 处理问题时发生错误: {e}")
        print(f"[错误类型] {type(e).__name__}")
        import traceback
        print(f"[错误详情] {traceback.format_exc()}")
    
    print("\n" + "="*60)
    print("🎉 演示完成!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(run_demo())
