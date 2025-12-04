"""
GeneratorController 代码生成器模块单元测试
"""
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlmodel import Session


class TestGeneratorController:
    """代码生成器控制器测试类"""
    
    def test_preview_not_found(self, client: TestClient):
        """测试预览不存在的表配置"""
        response = client.post("/Generator/preview", json={
            "table_id": 99999
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
    
    def test_download_not_found(self, client: TestClient):
        """测试下载不存在的表配置"""
        response = client.post("/Generator/download", json={
            "table_id": 99999
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
    
    def test_get_history(self, client: TestClient):
        """测试获取生成历史"""
        response = client.get("/Generator/history")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_get_history_by_table_id(self, client: TestClient):
        """测试按表ID获取生成历史"""
        response = client.get("/Generator/history?table_id=1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200


class TestGenTableController:
    """表配置控制器测试类"""
    
    def test_query_by_page(self, client: TestClient, session: Session):
        """测试分页查询表配置"""
        from generator.model.GenTable import GenTable
        
        table = GenTable(
            table_name="t_test_table",
            table_comment="测试表",
            class_name="TestTable",
            module_name="test",
            business_name="test_table",
            function_name="测试功能",
            create_time=datetime.now()
        )
        session.add(table)
        session.commit()
        
        response = client.post("/GenTable/queryByPage", json={
            "page": 1,
            "pageSize": 10
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_query_by_page_with_filter(self, client: TestClient, session: Session):
        """测试带过滤的分页查询"""
        from generator.model.GenTable import GenTable
        
        table = GenTable(
            table_name="t_user_info",
            table_comment="用户信息表",
            class_name="UserInfo",
            module_name="user",
            business_name="user_info",
            function_name="用户信息",
            create_time=datetime.now()
        )
        session.add(table)
        session.commit()
        
        response = client.post("/GenTable/queryByPage", json={
            "page": 1,
            "pageSize": 10,
            "table_name": "user"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_query_by_id(self, client: TestClient, session: Session):
        """测试根据ID查询表配置"""
        from generator.model.GenTable import GenTable
        
        table = GenTable(
            table_name="t_id_query",
            table_comment="ID查询表",
            class_name="IdQuery",
            module_name="test",
            business_name="id_query",
            function_name="ID查询",
            create_time=datetime.now()
        )
        session.add(table)
        session.commit()
        session.refresh(table)
        
        response = client.get(f"/GenTable/queryById?id={table.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_query_by_id_not_found(self, client: TestClient):
        """测试查询不存在的表配置"""
        response = client.get("/GenTable/queryById?id=99999")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
    
    def test_update_table(self, client: TestClient, session: Session):
        """测试更新表配置"""
        from generator.model.GenTable import GenTable
        
        table = GenTable(
            table_name="t_update_table",
            table_comment="待更新表",
            class_name="UpdateTable",
            module_name="test",
            business_name="update_table",
            function_name="更新功能",
            create_time=datetime.now()
        )
        session.add(table)
        session.commit()
        session.refresh(table)
        
        response = client.put("/GenTable/update", json={
            "id": table.id,
            "table_comment": "更新后的注释",
            "function_name": "更新后的功能名"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_update_table_not_found(self, client: TestClient):
        """测试更新不存在的表配置"""
        response = client.put("/GenTable/update", json={
            "id": 99999,
            "table_comment": "测试"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
    
    def test_delete_table(self, client: TestClient, session: Session):
        """测试删除表配置"""
        from generator.model.GenTable import GenTable
        
        table = GenTable(
            table_name="t_delete_table",
            table_comment="待删除表",
            class_name="DeleteTable",
            module_name="test",
            business_name="delete_table",
            function_name="删除功能",
            create_time=datetime.now()
        )
        session.add(table)
        session.commit()
        session.refresh(table)
        
        response = client.delete(f"/GenTable/delete?id={table.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_delete_table_not_found(self, client: TestClient):
        """测试删除不存在的表配置"""
        response = client.delete("/GenTable/delete?id=99999")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
    
    def test_get_db_tables(self, client: TestClient):
        """测试获取数据库可导入表"""
        response = client.get("/GenTable/dbTables")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200


class TestDbMetaService:
    """数据库元数据服务测试"""
    
    def test_map_python_type(self):
        """测试数据库类型映射到Python类型"""
        from generator.service.DbMetaService import DbMetaService
        
        service = DbMetaService()
        
        assert service._map_python_type("INTEGER") == "int"
        assert service._map_python_type("BIGINT") == "int"
        assert service._map_python_type("VARCHAR(255)") == "str"
        assert service._map_python_type("TEXT") == "str"
        assert service._map_python_type("FLOAT") == "float"
        assert service._map_python_type("DOUBLE") == "float"
        assert service._map_python_type("BOOLEAN") == "bool"
        assert service._map_python_type("DATETIME") == "datetime"
        assert service._map_python_type("DATE") == "date"
    
    def test_to_camel_case(self):
        """测试下划线转驼峰命名"""
        from generator.service.DbMetaService import DbMetaService
        
        service = DbMetaService()
        
        assert service._to_camel_case("user_name") == "userName"
        assert service._to_camel_case("create_time") == "createTime"
        assert service._to_camel_case("id") == "id"
    
    def test_to_pascal_case(self):
        """测试下划线转帕斯卡命名"""
        from generator.service.DbMetaService import DbMetaService
        
        service = DbMetaService()
        
        assert service._to_pascal_case("user_name") == "UserName"
        assert service._to_pascal_case("api_info") == "ApiInfo"
    
    def test_to_snake_case(self):
        """测试转下划线命名"""
        from generator.service.DbMetaService import DbMetaService
        
        service = DbMetaService()
        
        assert service._to_snake_case("UserName") == "user_name"
        assert service._to_snake_case("ApiInfo") == "api_info"
