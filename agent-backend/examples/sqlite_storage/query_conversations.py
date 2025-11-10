"""
查询对话历史工具

这个脚本用于查询SQLite数据库中存储的完整对话内容。
"""

import json
import sqlite3
from pathlib import Path


def query_conversations(db_path: str = "./data/langgraph.db", thread_id: str = None):
    """
    查询对话历史
    
    Args:
        db_path: 数据库文件路径
        thread_id: 线程ID，如果为None则查询所有线程
    """
    if not Path(db_path).exists():
        print(f"❌ 数据库文件不存在: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # 查询所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row["name"] for row in cursor.fetchall()]
        print("=" * 80)
        print(f"数据库: {db_path}")
        print(f"包含的表: {', '.join(tables)}")
        print("=" * 80)
        
        # 查询线程列表
        if thread_id:
            print(f"\n📋 查询线程: {thread_id}")
            thread_filter = f"WHERE thread_id = '{thread_id}'"
        else:
            print("\n📋 所有线程:")
            thread_filter = ""
        
        cursor.execute(f"""
            SELECT DISTINCT thread_id, COUNT(*) as message_count, 
                   MIN(created_at) as first_message, 
                   MAX(created_at) as last_message
            FROM conversation_messages
            {thread_filter}
            GROUP BY thread_id
            ORDER BY last_message DESC
        """)
        
        threads = cursor.fetchall()
        if not threads:
            print("  ❌ 没有找到对话记录")
            return
        
        print(f"\n找到 {len(threads)} 个线程:")
        for thread in threads:
            print(f"\n  线程ID: {thread['thread_id']}")
            print(f"  消息数: {thread['message_count']}")
            print(f"  首次对话: {thread['first_message']}")
            print(f"  最后对话: {thread['last_message']}")
        
        # 查询详细对话内容
        for thread in threads:
            tid = thread['thread_id']
            print("\n" + "=" * 80)
            print(f"💬 线程 [{tid}] 的完整对话内容:")
            print("=" * 80)
            
            cursor.execute("""
                SELECT id, checkpoint_id, message_type, role, content, metadata, created_at
                FROM conversation_messages
                WHERE thread_id = ?
                ORDER BY created_at ASC
            """, (tid,))
            
            messages = cursor.fetchall()
            for i, msg in enumerate(messages, 1):
                print(f"\n[消息 {i}] {msg['created_at']}")
                print(f"  角色: {msg['role']} ({msg['message_type']})")
                print(f"  内容: {msg['content']}")
                
                if msg['metadata']:
                    try:
                        metadata = json.loads(msg['metadata'])
                        if metadata:
                            print(f"  元数据: {json.dumps(metadata, ensure_ascii=False, indent=4)}")
                    except:
                        pass
                
                print(f"  Checkpoint ID: {msg['checkpoint_id']}")
        
        # 查询checkpoints统计
        print("\n" + "=" * 80)
        print("📊 Checkpoints 统计:")
        print("=" * 80)
        
        cursor.execute(f"""
            SELECT thread_id, COUNT(*) as checkpoint_count,
                   MIN(created_at) as first_checkpoint,
                   MAX(created_at) as last_checkpoint
            FROM checkpoints
            {thread_filter}
            GROUP BY thread_id
        """)
        
        for row in cursor.fetchall():
            print(f"\n  线程ID: {row['thread_id']}")
            print(f"  Checkpoint数: {row['checkpoint_count']}")
            print(f"  首次: {row['first_checkpoint']}")
            print(f"  最后: {row['last_checkpoint']}")
        
        # 查询store数据
        print("\n" + "=" * 80)
        print("💾 Store 数据:")
        print("=" * 80)
        
        cursor.execute("""
            SELECT namespace, key, value, created_at, updated_at
            FROM store_items
            ORDER BY updated_at DESC
        """)
        
        store_items = cursor.fetchall()
        if store_items:
            for item in store_items:
                print(f"\n  命名空间: {item['namespace']}")
                print(f"  键: {item['key']}")
                try:
                    value = json.loads(item['value'])
                    print(f"  值: {json.dumps(value, ensure_ascii=False, indent=4)}")
                except:
                    print(f"  值: {item['value']}")
                print(f"  创建时间: {item['created_at']}")
                print(f"  更新时间: {item['updated_at']}")
        else:
            print("  ❌ 没有store数据")
        
    finally:
        conn.close()


def main():
    """主函数"""
    import sys
    
    db_path = "./data/langgraph.db"
    thread_id = None
    
    # 解析命令行参数
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    if len(sys.argv) > 2:
        thread_id = sys.argv[2]
    
    query_conversations(db_path, thread_id)


if __name__ == "__main__":
    main()
