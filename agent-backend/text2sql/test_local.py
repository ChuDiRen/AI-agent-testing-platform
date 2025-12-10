"""本地测试脚本"""
import sys
from pathlib import Path

# 加载 .env 文件
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

sys.path.insert(0, "..")

from text2sql.database import setup_chinook, DatabaseConfig, register_connection
from text2sql.chat_graph import create_text2sql_graph


def test_query(query: str = "哪个音乐类型的曲目平均时长最长？"):
    """测试查询"""
    # 设置 Chinook 数据库
    db_path = setup_chinook()
    print(f"数据库路径: {db_path}")
    
    # 注册数据库连接
    config = DatabaseConfig(
        db_type="sqlite",
        database=str(db_path)
    )
    register_connection(0, config)
    print("数据库连接已注册")
    
    # 创建图
    graph = create_text2sql_graph(connection_id=0, dialect="sqlite")
    
    print(f"\n问题: {query}\n") 
    print("=" * 50)
    
    # 流式执行
    for event in graph.stream(
        {"messages": [{"role": "user", "content": query}]},
        {"configurable": {"thread_id": "test-1"}},
        stream_mode="updates"
    ):
        for node, output in event.items():
            print(f"\n--- [{node}] ---")
            if "messages" in output:
                for msg in output["messages"]:
                    if hasattr(msg, "content") and msg.content:
                        print(msg.content[:500])


if __name__ == "__main__":
    import sys
    query = sys.argv[1] if len(sys.argv) > 1 else "哪个音乐类型的曲目平均时长最长？"
    test_query(query)
