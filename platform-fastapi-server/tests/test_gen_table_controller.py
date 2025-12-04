"""
GenTableController 代码生成器表配置管理模块单元测试
覆盖所有接口: dbTables, importTables, queryByPage, queryById, update, delete
"""
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlmodel import Session
from unittest.mock import patch, MagicMock


class TestGenTableController:
    """代码生成器表配置控制器测试类"""

    @patch('generator.service.DbMetaService.DbMetaService.get_all_tables')
    def test_get_db_tables_success(self, mock_get_tables, client: TestClient, session: Session, admin_headers):
        """测试获取数据库表列表成功"""
        from generator.model.GenTable import GenTable

        # 模拟数据库返回的表列表
        mock_tables = ["users", "roles", "permissions", "test_table"]
        mock_get_tables.return_value = mock_tables

        # 在数据库中创建已导入的表
        existing_table = GenTable(
            table_name="users",
            table_comment="用户表",
            class_name="Users",
            business_name="users",
            function_name="用户表",
            create_time=datetime.now()
        )
        session.add(existing_table)
        session.commit()

        response = client.get("/GenTable/dbTables",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "list" in data["data"]

        # 验证返回的是未导入的表
        returned_tables = data["data"]["list"]
        assert "users" not in returned_tables  # 已导入的表应该被过滤掉
        assert "roles" in returned_tables
        assert "permissions" in returned_tables

    @patch('generator.service.DbMetaService.DbMetaService.get_all_tables')
    def test_get_db_tables_error(self, mock_get_tables, client: TestClient, admin_headers):
        """测试获取数据库表列表时出错"""
        mock_get_tables.side_effect = Exception("数据库连接失败")

        response = client.get("/GenTable/dbTables",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
        assert "错误" in data["msg"]

    @patch('generator.service.DbMetaService.DbMetaService')
    def test_import_tables_success(self, mock_db_service, client: TestClient, session: Session, admin_headers):
        """测试批量导入表配置成功"""
        from generator.model.GenTable import GenTable
        from generator.model.GenTableColumn import GenTableColumn

        # 模拟数据库服务返回的表信息和字段信息
        mock_table_info = {
            'table_comment': '测试表',
            'table_name': 'test_table'
        }

        mock_columns = [
            {
                'column_name': 'id',
                'column_comment': '主键ID',
                'column_type': 'int',
                'column_length': 11,
                'is_nullable': 'NO',
                'column_default': None,
                'sort': 1
            },
            {
                'column_name': 'name',
                'column_comment': '名称',
                'column_type': 'varchar',
                'column_length': 50,
                'is_nullable': 'YES',
                'column_default': None,
                'sort': 2
            }
        ]

        mock_service_instance = MagicMock()
        mock_service_instance.get_table_info.return_value = mock_table_info
        mock_service_instance.get_column_details.return_value = mock_columns
        mock_db_service.return_value = mock_service_instance

        import_request = {
            "table_names": ["test_table", "another_table"]
        }

        response = client.post("/GenTable/importTables",
            json=import_request,
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "成功" in data["msg"]
        assert "2" in data["msg"]  # 导入了2张表

    @patch('generator.service.DbMetaService.DbMetaService')
    def test_import_tables_existing_table(self, mock_db_service, client: TestClient, session: Session, admin_headers):
        """测试导入已存在的表"""
        from generator.model.GenTable import GenTable

        # 先创建一个已存在的表
        existing_table = GenTable(
            table_name="existing_table",
            table_comment="已存在的表",
            class_name="ExistingTable",
            business_name="existing_table",
            function_name="已存在的表",
            create_time=datetime.now()
        )
        session.add(existing_table)
        session.commit()

        mock_service_instance = MagicMock()
        mock_service_instance.get_table_info.return_value = {
            'table_comment': '已存在的表',
            'table_name': 'existing_table'
        }
        mock_service_instance.get_column_details.return_value = []
        mock_db_service.return_value = mock_service_instance

        import_request = {
            "table_names": ["existing_table", "new_table"]
        }

        response = client.post("/GenTable/importTables",
            json=import_request,
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        # 应该只导入新表，跳过已存在的表
        assert "1" in data["msg"]

    @patch('generator.service.DbMetaService.DbMetaService')
    def test_import_tables_table_not_found(self, mock_db_service, client: TestClient, admin_headers):
        """测试导入不存在的表"""
        mock_service_instance = MagicMock()
        mock_service_instance.get_table_info.return_value = None  # 表不存在
        mock_db_service.return_value = mock_service_instance

        import_request = {
            "table_names": ["nonexistent_table"]
        }

        response = client.post("/GenTable/importTables",
            json=import_request,
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        # 没有导入任何表
        assert "0" in data["msg"]

    def test_query_by_page_success(self, client: TestClient, session: Session, admin_headers):
        """测试分页查询表配置成功"""
        from generator.model.GenTable import GenTable

        # 创建测试表配置
        tables = [
            GenTable(
                table_name="users",
                table_comment="用户表",
                class_name="Users",
                business_name="users",
                function_name="用户表",
                create_time=datetime.now()
            ),
            GenTable(
                table_name="roles",
                table_comment="角色表",
                class_name="Roles",
                business_name="roles",
                function_name="角色表",
                create_time=datetime.now()
            ),
            GenTable(
                table_name="permissions",
                table_comment="权限表",
                class_name="Permissions",
                business_name="permissions",
                function_name="权限表",
                create_time=datetime.now()
            )
        ]

        for table in tables:
            session.add(table)
        session.commit()

        response = client.post("/GenTable/queryByPage",
            json={"page": 1, "pageSize": 10},
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "list" in data["data"]
        assert "total" in data["data"]
        assert len(data["data"]["list"]) >= 3

    def test_query_by_page_with_filter(self, client: TestClient, session: Session, admin_headers):
        """测试带过滤条件的分页查询"""
        from generator.model.GenTable import GenTable

        # 创建测试表配置
        tables = [
            GenTable(
                table_name="test_users",
                table_comment="测试用户表",
                class_name="TestUsers",
                business_name="test_users",
                function_name="测试用户表",
                create_time=datetime.now()
            ),
            GenTable(
                table_name="test_roles",
                table_comment="测试角色表",
                class_name="TestRoles",
                business_name="test_roles",
                function_name="测试角色表",
                create_time=datetime.now()
            ),
            GenTable(
                table_name="normal_table",
                table_comment="普通表",
                class_name="NormalTable",
                business_name="normal_table",
                function_name="普通表",
                create_time=datetime.now()
            )
        ]

        for table in tables:
            session.add(table)
        session.commit()

        # 按表名过滤
        response = client.post("/GenTable/queryByPage",
            json={
                "page": 1,
                "pageSize": 10,
                "table_name": "test_"
            },
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert len(data["data"]["list"]) >= 2
        # 验证返回的都是包含"test_"的表
        for table in data["data"]["list"]:
            assert "test_" in table["table_name"]

        # 按表注释过滤
        response = client.post("/GenTable/queryByPage",
            json={
                "page": 1,
                "pageSize": 10,
                "table_comment": "测试"
            },
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        if len(data["data"]["list"]) > 0:
            for table in data["data"]["list"]:
                assert "测试" in table["table_comment"]

    def test_query_by_id_success(self, client: TestClient, session: Session, admin_headers):
        """测试根据ID查询表配置成功"""
        from generator.model.GenTable import GenTable
        from generator.model.GenTableColumn import GenTableColumn

        # 创建表配置
        table = GenTable(
            table_name="test_table",
            table_comment="测试表",
            class_name="TestTable",
            business_name="test_table",
            function_name="测试表",
            create_time=datetime.now()
        )
        session.add(table)
        session.commit()

        # 创建字段配置
        columns = [
            GenTableColumn(
                table_id=table.id,
                column_name="id",
                column_comment="主键",
                column_type="int",
                column_length=11,
                is_nullable="NO",
                sort=1,
                create_time=datetime.now()
            ),
            GenTableColumn(
                table_id=table.id,
                column_name="name",
                column_comment="名称",
                column_type="varchar",
                column_length=50,
                is_nullable="YES",
                sort=2,
                create_time=datetime.now()
            )
        ]

        for col in columns:
            session.add(col)
        session.commit()

        response = client.get(f"/GenTable/queryById?id={table.id}",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "table" in data["data"]
        assert "columns" in data["data"]
        assert data["data"]["table"]["table_name"] == "test_table"
        assert len(data["data"]["columns"]) >= 2

    def test_query_by_id_not_found(self, client: TestClient, admin_headers):
        """测试查询不存在的表配置ID"""
        response = client.get("/GenTable/queryById?id=99999",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
        assert "不存在" in data["msg"]

    def test_update_table_success(self, client: TestClient, session: Session, admin_headers):
        """测试更新表配置成功"""
        from generator.model.GenTable import GenTable

        # 创建表配置
        table = GenTable(
            table_name="test_table",
            table_comment="测试表",
            class_name="TestTable",
            business_name="test_table",
            function_name="测试表",
            create_time=datetime.now()
        )
        session.add(table)
        session.commit()

        update_data = {
            "id": table.id,
            "table_comment": "更新后的测试表",
            "function_name": "更新后的功能名称",
            "class_name": "UpdatedTestTable"
        }

        response = client.put("/GenTable/update",
            json=update_data,
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "成功" in data["msg"]

    def test_update_table_not_found(self, client: TestClient, admin_headers):
        """测试更新不存在的表配置"""
        update_data = {
            "id": 99999,
            "table_comment": "不存在的表"
        }

        response = client.put("/GenTable/update",
            json=update_data,
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
        assert "不存在" in data["msg"]

    def test_delete_table_success(self, client: TestClient, session: Session, admin_headers):
        """测试删除表配置成功"""
        from generator.model.GenTable import GenTable
        from generator.model.GenTableColumn import GenTableColumn

        # 创建表配置
        table = GenTable(
            table_name="delete_table",
            table_comment="待删除表",
            class_name="DeleteTable",
            business_name="delete_table",
            function_name="待删除表",
            create_time=datetime.now()
        )
        session.add(table)
        session.commit()

        # 创建字段配置
        column = GenTableColumn(
            table_id=table.id,
            column_name="id",
            column_comment="主键",
            column_type="int",
            column_length=11,
            is_nullable="NO",
            sort=1,
            create_time=datetime.now()
        )
        session.add(column)
        session.commit()

        response = client.delete(f"/GenTable/delete?id={table.id}",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "成功" in data["msg"]

    def test_delete_table_not_found(self, client: TestClient, admin_headers):
        """测试删除不存在的表配置"""
        response = client.delete("/GenTable/delete?id=99999",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
        assert "不存在" in data["msg"]

    def test_unauthorized_access(self, client: TestClient):
        """测试未授权访问"""
        response = client.get("/GenTable/dbTables")

        # 应该返回401未授权或被重定向
        assert response.status_code in [401, 403, 302]

    def test_unauthorized_import(self, client: TestClient):
        """测试未授权的导入操作"""
        import_request = {
            "table_names": ["test_table"]
        }

        response = client.post("/GenTable/importTables",
            json=import_request
        )

        # 应该返回401未授权或被重定向
        assert response.status_code in [401, 403, 302]


class TestGenTableIntegration:
    """代码生成器表配置集成测试"""

    @patch('generator.service.DbMetaService.DbMetaService')
    def test_full_import_workflow(self, mock_db_service, client: TestClient, session: Session, admin_headers):
        """测试完整的导入工作流程"""
        from generator.model.GenTable import GenTable

        # 模拟数据库服务
        mock_table_info = {
            'table_comment': '完整工作流测试表',
            'table_name': 'workflow_test'
        }

        mock_columns = [
            {
                'column_name': 'id',
                'column_comment': '主键',
                'column_type': 'int',
                'column_length': 11,
                'is_nullable': 'NO',
                'column_default': None,
                'sort': 1
            }
        ]

        mock_service_instance = MagicMock()
        mock_service_instance.get_table_info.return_value = mock_table_info
        mock_service_instance.get_column_details.return_value = mock_columns
        mock_db_service.return_value = mock_service_instance

        # 1. 获取可导入的表
        mock_service_instance.get_all_tables.return_value = ["workflow_test", "other_table"]

        response = client.get("/GenTable/dbTables",
            headers=admin_headers
        )
        assert response.status_code == 200

        # 2. 导入表
        import_request = {
            "table_names": ["workflow_test"]
        }

        response = client.post("/GenTable/importTables",
            json=import_request,
            headers=admin_headers
        )
        assert response.status_code == 200
        assert data["code"] == 200

        # 3. 查询导入的表
        table = session.exec(select(GenTable).where(GenTable.table_name == "workflow_test")).first()
        assert table is not None

        response = client.get(f"/GenTable/queryById?id={table.id}",
            headers=admin_headers
        )
        assert response.status_code == 200

        # 4. 更新表配置
        update_data = {
            "id": table.id,
            "table_comment": "更新后的工作流测试表"
        }

        response = client.put("/GenTable/update",
            json=update_data,
            headers=admin_headers
        )
        assert response.status_code == 200
        assert data["code"] == 200

        # 5. 删除表配置
        response = client.delete(f"/GenTable/delete?id={table.id}",
            headers=admin_headers
        )
        assert response.status_code == 200
        assert data["code"] == 200