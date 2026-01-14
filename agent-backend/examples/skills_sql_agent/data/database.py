"""
数据库管理模块
负责数据库的创建、连接和数据填充（纯异步实现）
"""

import aiosqlite
from pathlib import Path
from datetime import datetime, timedelta


class DatabaseManager:
    """数据库管理器（纯异步实现）"""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    async def setup_database(self) -> None:
        """创建示例数据库（异步）"""
        if self.db_path.exists():
            print(f"[数据库] 数据库已存在: {self.db_path}")
            return

        print(f"[数据库] 创建示例数据库: {self.db_path}")
        async with aiosqlite.connect(str(self.db_path)) as conn:
            cursor = await conn.cursor()

            # 创建表结构
            await self._create_tables(cursor)

            # 填充示例数据
            await self._populate_sample_data(cursor)

            await conn.commit()

        print(f"[成功] 示例数据填充完成")
        print(f"  - 客户数: 8")
        print(f"  - 产品数: 8")
        print(f"  - 仓库数: 4")
        print(f"  - 订单数: 50")

    async def _create_tables(self, cursor) -> None:
        """创建数据库表结构（异步）"""
        # 客户表
        await cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT,
                signup_date TEXT,
                status TEXT DEFAULT 'active',
                customer_tier TEXT DEFAULT 'bronze'
            )
        """)

        # 产品表
        await cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                sku TEXT,
                category TEXT,
                unit_price REAL,
                cost_price REAL,
                supplier_id INTEGER
            )
        """)

        # 仓库表
        await cursor.execute("""
            CREATE TABLE IF NOT EXISTS warehouses (
                warehouse_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                location TEXT,
                type TEXT DEFAULT 'branch'
            )
        """)

        # 订单表
        await cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY,
                customer_id INTEGER,
                order_date TEXT,
                status TEXT DEFAULT 'pending',
                total_amount REAL,
                sales_region TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
            )
        """)

        # 订单项表
        await cursor.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                item_id INTEGER PRIMARY KEY,
                order_id INTEGER,
                product_id INTEGER,
                quantity INTEGER,
                unit_price REAL,
                discount_percent REAL DEFAULT 0,
                FOREIGN KEY (order_id) REFERENCES orders(order_id)
            )
        """)

        # 库存表
        await cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                inventory_id INTEGER PRIMARY KEY,
                product_id INTEGER,
                warehouse_id INTEGER,
                quantity INTEGER DEFAULT 0,
                reserved_quantity INTEGER DEFAULT 0,
                reorder_level INTEGER DEFAULT 10,
                last_restocked TEXT,
                FOREIGN KEY (product_id) REFERENCES products(product_id),
                FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id)
            )
        """)

        # 库存变动表
        await cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_movements (
                movement_id INTEGER PRIMARY KEY,
                product_id INTEGER,
                warehouse_id INTEGER,
                movement_type TEXT,
                quantity INTEGER,
                movement_date TEXT,
                reference TEXT,
                FOREIGN KEY (product_id) REFERENCES products(product_id),
                FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id)
            )
        """)

    async def _populate_sample_data(self, cursor) -> None:
        """填充示例数据（异步）"""
        base_date = datetime.now() - timedelta(days=180)

        # 插入客户数据
        await cursor.executemany("""
            INSERT INTO customers (name, email, signup_date, status, customer_tier) VALUES (?, ?, ?, ?, ?)
        """, [
            ("张伟", "zhangwei@example.com", (base_date - timedelta(days=120)).strftime("%Y-%m-%d"), "active", "platinum"),
            ("李娜", "lina@example.com", (base_date - timedelta(days=90)).strftime("%Y-%m-%d"), "active", "gold"),
            ("王芳", "wangfang@example.com", (base_date - timedelta(days=60)).strftime("%Y-%m-%d"), "active", "silver"),
            ("刘强", "liuqiang@example.com", (base_date - timedelta(days=30)).strftime("%Y-%m-%d"), "active", "bronze"),
            ("陈静", "chenjing@example.com", (base_date - timedelta(days=100)).strftime("%Y-%m-%d"), "active", "gold"),
            ("赵敏", "zhaomin@example.com", (base_date - timedelta(days=20)).strftime("%Y-%m-%d"), "active", "bronze"),
            ("孙洋", "sunyang@example.com", (base_date - timedelta(days=150)).strftime("%Y-%m-%d"), "inactive", "silver"),
            ("周杰", "zhoujie@example.com", (base_date - timedelta(days=80)).strftime("%Y-%m-%d"), "active", "platinum"),
        ])

        # 插入产品数据
        await cursor.executemany("""
            INSERT INTO products (name, sku, category, unit_price, cost_price, supplier_id) VALUES (?, ?, ?, ?, ?, ?)
        """, [
            ("智能手机 X1", "SKU-PHONE-001", "电子产品", 5999, 3500, 1),
            ("笔记本电脑 Pro", "SKU-LAPTOP-001", "电子产品", 12999, 8000, 1),
            ("无线耳机", "SKU-AUDIO-001", "配件", 899, 300, 2),
            ("蓝牙音箱", "SKU-AUDIO-002", "配件", 1299, 500, 2),
            ("机械键盘", "SKU-ACC-001", "配件", 1599, 800, 3),
            ("4K 显示器", "SKU-DISP-001", "电子产品", 3999, 2500, 3),
            ("智能手表", "SKU-WATCH-001", "可穿戴设备", 2499, 1200, 4),
            ("平板电脑", "SKU-TABLET-001", "电子产品", 4999, 3000, 4),
        ])

        # 插入仓库数据
        await cursor.executemany("""
            INSERT INTO warehouses (name, location, type) VALUES (?, ?, ?)
        """, [
            ("北京主仓", "北京市朝阳区", "main"),
            ("上海分仓", "上海市浦东新区", "branch"),
            ("广州分仓", "广州市天河区", "branch"),
            ("深圳临时仓", "深圳市南山区", "temporary"),
        ])

        # 插入订单数据
        sales_regions = ["north", "south", "east", "west"]
        statuses = ["completed", "completed", "completed", "pending", "cancelled"]

        for i in range(50):
            customer_id = (i % 8) + 1
            order_date = (base_date + timedelta(days=i * 3)).strftime("%Y-%m-%d")
            status = statuses[i % len(statuses)]
            sales_region = sales_regions[i % len(sales_regions)]

            total_amount = 1000 + (i * 500) + (i % 7) * 1000

            await cursor.execute("""
                INSERT INTO orders (customer_id, order_date, status, total_amount, sales_region) VALUES (?, ?, ?, ?, ?)
            """, (customer_id, order_date, status, total_amount, sales_region))

            order_id = cursor.lastrowid

            num_items = (i % 3) + 1
            for j in range(num_items):
                product_id = (i + j) % 8 + 1
                quantity = (j + 1)
                unit_price = 500 + (product_id * 500)
                discount = (i % 5) * 5

                await cursor.execute("""
                    INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_percent) VALUES (?, ?, ?, ?, ?)
                """, (order_id, product_id, quantity, unit_price, discount))

        # 插入库存数据
        reorder_levels = [5, 10, 15, 20]
        for product_id in range(1, 9):
            for warehouse_id in range(1, 5):
                quantity = 5 + (product_id * 3) + (warehouse_id * 5)
                reorder_level = reorder_levels[warehouse_id - 1]
                last_restocked = (base_date + timedelta(days=product_id * 10)).strftime("%Y-%m-%d")

                await cursor.execute("""
                    INSERT INTO inventory (product_id, warehouse_id, quantity, reserved_quantity, reorder_level, last_restocked)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (product_id, warehouse_id, quantity, (i % 3) + 1, reorder_level, last_restocked))
