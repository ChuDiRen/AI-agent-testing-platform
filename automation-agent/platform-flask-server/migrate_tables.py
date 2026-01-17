"""数据库表结构迁移脚本"""
from app import application, database

with application.app_context():
    print("开始数据库迁移...")

    # t_user 表的新列
    columns = [
        ("alias", "VARCHAR(30)"),
        ("email", "VARCHAR(255) NOT NULL DEFAULT ''"),
        ("phone", "VARCHAR(20)"),
        ("is_active", "TINYINT(1) DEFAULT 1"),
        ("is_superuser", "TINYINT(1) DEFAULT 0"),
        ("last_login", "DATETIME"),
        ("dept_id", "INT"),
        ("created_at", "DATETIME DEFAULT CURRENT_TIMESTAMP"),
        ("updated_at", "DATETIME"),
    ]

    for col_name, col_type in columns:
        try:
            database.session.execute(
                database.text(f"ALTER TABLE t_user ADD COLUMN {col_name} {col_type}")
            )
            print(f"✓ 添加 {col_name} 列")
        except Exception as e:
            print(f"  {col_name} 列: {str(e)[:50]}")

    # 创建新表
    new_tables = [
        ("t_role", """
            CREATE TABLE IF NOT EXISTS t_role (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(20) UNIQUE NOT NULL,
                desc VARCHAR(500),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP
            )
        """),
        ("t_api", """
            CREATE TABLE IF NOT EXISTS t_api (
                id INT AUTO_INCREMENT PRIMARY KEY,
                path VARCHAR(100) NOT NULL,
                method VARCHAR(10) NOT NULL,
                summary VARCHAR(500),
                tags VARCHAR(100),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP
            )
        """),
        ("t_menu", """
            CREATE TABLE IF NOT EXISTS t_menu (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(20) NOT NULL,
                remark JSON,
                menu_type VARCHAR(20),
                icon VARCHAR(100),
                path VARCHAR(100) NOT NULL,
                `order` INT DEFAULT 0,
                parent_id INT DEFAULT 0,
                is_hidden TINYINT(1) DEFAULT 0,
                component VARCHAR(100) NOT NULL,
                keepalive TINYINT(1) DEFAULT 1,
                redirect VARCHAR(100),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP
            )
        """),
        ("t_dept", """
            CREATE TABLE IF NOT EXISTS t_dept (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(20) UNIQUE NOT NULL,
                desc VARCHAR(500),
                is_deleted TINYINT(1) DEFAULT 0,
                `order` INT DEFAULT 0,
                parent_id INT DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP
            )
        """),
        ("t_dept_closure", """
            CREATE TABLE IF NOT EXISTS t_dept_closure (
                id INT AUTO_INCREMENT PRIMARY KEY,
                ancestor INT NOT NULL,
                descendant INT NOT NULL,
                `level` INT DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP
            )
        """),
        ("t_audit_log", """
            CREATE TABLE IF NOT EXISTS t_audit_log (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                username VARCHAR(64) DEFAULT '',
                module VARCHAR(64) DEFAULT '',
                summary VARCHAR(128) DEFAULT '',
                method VARCHAR(10) DEFAULT '',
                path VARCHAR(255) DEFAULT '',
                status INT DEFAULT -1,
                response_time INT DEFAULT 0,
                request_args JSON,
                response_body JSON,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP
            )
        """),
        ("t_user_role", """
            CREATE TABLE IF NOT EXISTS t_user_role (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                role_id INT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """),
        ("t_role_menu", """
            CREATE TABLE IF NOT EXISTS t_role_menu (
                id INT AUTO_INCREMENT PRIMARY KEY,
                role_id INT NOT NULL,
                menu_id INT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """),
        ("t_role_api", """
            CREATE TABLE IF NOT EXISTS t_role_api (
                id INT AUTO_INCREMENT PRIMARY KEY,
                role_id INT NOT NULL,
                api_id INT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """),
    ]

    for table_name, create_sql in new_tables:
        try:
            database.session.execute(database.text(create_sql))
            print(f"✓ 创建/更新 {table_name} 表")
        except Exception as e:
            print(f"  {table_name}: {str(e)[:50]}")

    database.session.commit()
    print("\n数据库迁移完成！")
