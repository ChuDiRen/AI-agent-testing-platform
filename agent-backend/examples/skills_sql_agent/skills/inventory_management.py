"""
库存管理技能
包含库存管理的数据库模式和业务逻辑
"""

from typing import TypedDict

class InventoryManagementSkill(TypedDict):
    """库存管理技能定义"""
    name: str
    description: str
    content: str

def get_inventory_management_skill() -> InventoryManagementSkill:
    """获取库存管理技能"""
    return {
        "name": "inventory_management",
        "description": "库存管理的数据库模式和业务逻辑，包括产品、仓库和库存水平。",
        "content": """# 库存管理技能

## 数据库表结构
### products（产品表）
- product_id (主键): 产品唯一标识
- product_name: 产品名称
- sku: SKU 编码
- category: 产品类别
- unit_cost: 单位成本
- reorder_point: 补货点（补货前的最低库存水平）
- discontinued: 是否停产 (boolean)

### warehouses（仓库表）
- warehouse_id (主键): 仓库唯一标识
- warehouse_name: 仓库名称
- location: 仓库位置
- capacity: 仓库容量

### inventory（库存表）
- inventory_id (主键): 库存记录唯一标识
- product_id (外键 -> products): 产品ID
- warehouse_id (外键 -> warehouses): 仓库ID
- quantity_on_hand: 现有库存数量
- last_updated: 最后更新时间

### stock_movements（库存变动表）
- movement_id (主键): 库存变动唯一标识
- product_id (外键 -> products): 产品ID
- warehouse_id (外键 -> warehouses): 仓库ID
- movement_type: 变动类型 (inbound/outbound/transfer/adjustment)
- quantity: 变动数量 (入库为正，出库为负)
- movement_date: 变动日期
- reference_number: 参考编号

## 业务规则
**可用库存**: quantity_on_hand from inventory table where quantity_on_hand > 0
**需要补货的产品**: 所有仓库的总 quantity_on_hand 小于或等于产品的 reorder_point
**活跃产品原则**: 排除 discontinued = true 的产品，除非特别分析停产产品
**库存价值计算**: quantity_on_hand * unit_cost for each product

## 示例查询
-- 查找所有仓库中低于补货点的产品
SELECT p.product_id, p.product_name, p.reorder_point, SUM(i.quantity_on_hand) as total_stock, p.unit_cost, (p.reorder_point - SUM(i.quantity_on_hand)) as units_to_reorder
FROM products p
JOIN inventory i ON p.product_id = i.product_id
WHERE p.discontinued = false
GROUP BY p.product_id, p.product_name, p.reorder_point, p.unit_cost
HAVING SUM(i.quantity_on_hand) <= p.reorder_point
ORDER BY units_to_reorder DESC;
"""
    }
