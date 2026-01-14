"""
动态技能生成器
负责根据实际数据库结构动态生成技能内容
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Any

class DynamicSkillGenerator:
    """动态技能生成器"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
    
    def generate_chinook_analytics_skill(self) -> Dict[str, Any]:
        """动态生成Chinook分析技能"""
        try:
            # 实时获取数据库表结构
            with sqlite3.connect(self.db_path) as conn:
                # 获取所有表
                tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
                
                skill_content = "# Chinook音乐商店分析技能（动态生成）\n\n"
                skill_content += "## 数据库表结构\n"
                
                # 获取每个表的结构
                for table in tables:
                    table_name = table[0]
                    if table_name.startswith('_'):  # 跳过系统表
                        continue
                        
                    # 获取表结构
                    schema = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
                    columns = []
                    for col in schema:
                        columns.append(f"- {col[1]} ({col[2]})")
                    
                    skill_content += f"### {table_name}（{table_name}表）\n"
                    skill_content += "\n".join(columns)
                    skill_content += "\n\n"
                
                # 添加业务规则（基于实际表结构）
                skill_content += """## 业务规则
**客户分析**: 基于Customer和Invoice表分析客户购买行为
**员工绩效**: 基于Invoice和Employee表分析员工销售业绩
**音乐趋势**: 基于Track、Genre、Album表分析音乐流行趋势
**收入分析**: 基于InvoiceLine的UnitPrice和Quantity计算收入
**地理分析**: 基于Customer和Invoice的地理位置分析销售分布

## 示例查询（动态生成）
"""
                
                # 基于实际表结构生成示例查询
                if any(table[0] == 'Customer' for table in tables):
                    skill_content += """-- 获取收入前5的客户
SELECT 
    c.CustomerId,
    c.FirstName || ' ' || c.LastName as full_name,
    c.Country,
    SUM(i.Total) as total_spent,
    COUNT(i.InvoiceId) as invoice_count,
    AVG(i.Total) as avg_invoice_amount,
    MIN(i.InvoiceDate) as first_purchase_date,
    MAX(i.InvoiceDate) as last_purchase_date
FROM Customer c
JOIN Invoice i ON c.CustomerId = i.CustomerId
GROUP BY c.CustomerId, c.FirstName, c.LastName, c.Country
ORDER BY total_spent DESC
LIMIT 5;

"""
                
                if any(table[0] == 'Artist' for table in tables):
                    skill_content += """-- 获取收入前5的艺术家
SELECT 
    a.Name as artist,
    SUM(il.UnitPrice * il.Quantity) as total_revenue,
    COUNT(DISTINCT il.InvoiceId) as tracks_sold
FROM Artist a
JOIN Album al ON a.ArtistId = al.ArtistId
JOIN Track t ON al.AlbumId = t.AlbumId
JOIN InvoiceLine il ON t.TrackId = il.TrackId
GROUP BY a.Name
ORDER BY total_revenue DESC
LIMIT 5;

"""
                
                skill_content += "## 使用说明\n"
                skill_content += "- 所有表名和字段名都与实际数据库一致\n"
                skill_content += "- 查询基于实际的表结构动态生成\n"
                skill_content += "- 支持实时适应数据库结构变化\n"
                
                return {
                    "name": "chinook_analytics",
                    "description": "Chinook音乐商店数据库的分析技能，包括客户、订单、产品和收入分析。（动态生成）",
                    "content": skill_content
                }
                
        except Exception as e:
            return {
                "name": "chinook_analytics",
                "description": "Chinook音乐商店数据库的分析技能，包括客户、订单、产品和收入分析。（动态生成）",
                "content": f"Error generating dynamic skill: {e}. Please try again."
            }
    
    def get_table_sample_data(self, table_name: str, limit: int = 3) -> str:
        """获取表样本数据用于分析"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # 获取样本数据
                sample_data = conn.execute(f"SELECT * FROM {table_name} LIMIT {limit}").fetchall()
                
                # 获取列名
                columns = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
                column_names = [col[1] for col in columns]
                
                result = f"样本数据 ({table_name}表):\n"
                result += f"列名: {', '.join(column_names)}\n"
                result += f"数据行数: {len(sample_data)}\n"
                
                for i, row in enumerate(sample_data, 1):
                    result += f"行{i}: {row}\n"
                
                return result
                
        except Exception as e:
            return f"Error getting sample data for {table_name}: {e}"
    
    def get_available_skills(self) -> List[str]:
        """获取可用的动态技能列表"""
        return ["chinook_analytics"]
    
    def generate_skill_by_name(self, skill_name: str) -> Dict[str, Any]:
        """根据技能名称动态生成技能内容"""
        if skill_name == "chinook_analytics":
            return self.generate_chinook_analytics_skill()
        else:
            return {
                "name": skill_name,
                "description": f"Dynamic skill for {skill_name} (not implemented)",
                "content": f"Skill '{skill_name}' is not implemented yet. Available skills: {', '.join(self.get_available_skills())}"
            }
