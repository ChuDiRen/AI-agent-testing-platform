"""
销售分析技能
包含销售数据分析的数据库模式和业务逻辑
"""

from typing import TypedDict

class SalesAnalyticsSkill(TypedDict):
    """销售分析技能定义"""
    name: str
    description: str
    content: str

def get_sales_analytics_skill() -> SalesAnalyticsSkill:
    """获取销售分析技能"""
    return {
        "name": "sales_analytics",
        "description": "销售数据分析的数据库模式和业务逻辑，包括客户、订单和收入。",
        "content": """# 销售分析技能

## 数据库表结构
### customers（客户表）
- customer_id (主键): 客户唯一标识
- name: 客户姓名
- email: 客户邮箱
- signup_date: 注册日期
- status: 状态 (active/inactive)
- customer_tier: 客户层级 (bronze/silver/gold/platinum)

### orders（订单表）
- order_id (主键): 订单唯一标识
- customer_id (外键 -> customers): 客户ID
- order_date: 订单日期
- status: 订单状态 (pending/completed/cancelled/refunded)
- total_amount: 订单总金额
- sales_region: 销售区域 (north/south/east/west)

### order_items（订单项表）
- item_id (主键): 订单项唯一标识
- order_id (外键 -> orders): 订单ID
- product_id: 产品ID
- quantity: 数量
- unit_price: 单价
- discount_percent: 折扣百分比

## 业务规则
**活跃客户定义**: status = 'active' AND signup_date <= CURRENT_DATE - INTERVAL '90 days'
**收入计算规则**: 只计算状态为 'completed' 的订单。使用 orders 表的 total_amount，该值已包含折扣。
**客户生命周期价值 (CLV)**: 某客户所有已完成订单的总金额
**高价值订单定义**: total_amount > 1000 的订单

## 示例查询
-- 获取上季度收入前 10 的客户
SELECT c.customer_id, c.name, c.customer_tier, SUM(o.total_amount) as total_revenue
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.status = 'completed'
  AND o.order_date >= CURRENT_DATE - INTERVAL '3 months'
GROUP BY c.customer_id, c.name, c.customer_tier
ORDER BY total_revenue DESC
LIMIT 10;
"""
    }
