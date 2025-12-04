"""
PromptTemplateController 提示词模板模块单元测试
"""
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlmodel import Session


class TestPromptTemplateController:
    """提示词模板控制器测试类"""
    
    def test_query_by_page(self, client: TestClient, session: Session):
        """测试分页查询提示词模板"""
        from aiassistant.model.PromptTemplate import PromptTemplate
        
        template = PromptTemplate(
            name="测试模板",
            test_type="API",
            template_type="system",
            content="这是测试内容",
            is_active=True,
            create_time=datetime.now()
        )
        session.add(template)
        session.commit()
        
        response = client.post("/PromptTemplate/queryByPage", json={
            "page": 1,
            "pageSize": 10
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_query_by_page_with_filter(self, client: TestClient, session: Session):
        """测试带过滤的分页查询"""
        from aiassistant.model.PromptTemplate import PromptTemplate
        
        template = PromptTemplate(
            name="API测试模板",
            test_type="API",
            template_type="system",
            content="API测试内容",
            is_active=True,
            create_time=datetime.now()
        )
        session.add(template)
        session.commit()
        
        response = client.post("/PromptTemplate/queryByPage", json={
            "page": 1,
            "pageSize": 10,
            "test_type": "API"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_query_by_id(self, client: TestClient, session: Session):
        """测试根据ID查询提示词模板"""
        from aiassistant.model.PromptTemplate import PromptTemplate
        
        template = PromptTemplate(
            name="ID查询模板",
            test_type="API",
            template_type="system",
            content="测试内容",
            is_active=True,
            create_time=datetime.now()
        )
        session.add(template)
        session.commit()
        session.refresh(template)
        
        response = client.get(f"/PromptTemplate/queryById?id={template.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["name"] == "ID查询模板"
    
    def test_query_by_id_not_found(self, client: TestClient):
        """测试查询不存在的提示词模板"""
        response = client.get("/PromptTemplate/queryById?id=99999")
        
        assert response.status_code == 200
        data = response.json()
        assert "没有数据" in data.get("msg", "")
    
    def test_query_by_type(self, client: TestClient, session: Session):
        """测试按测试类型查询模板"""
        from aiassistant.model.PromptTemplate import PromptTemplate
        
        template = PromptTemplate(
            name="Web测试模板",
            test_type="Web",
            template_type="system",
            content="Web测试内容",
            is_active=True,
            create_time=datetime.now()
        )
        session.add(template)
        session.commit()
        
        response = client.get("/PromptTemplate/queryByType?testType=Web")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_query_all(self, client: TestClient, session: Session):
        """测试查询所有模板"""
        from aiassistant.model.PromptTemplate import PromptTemplate
        
        template = PromptTemplate(
            name="全部查询模板",
            test_type="API",
            template_type="system",
            content="测试内容",
            is_active=True,
            create_time=datetime.now()
        )
        session.add(template)
        session.commit()
        
        response = client.get("/PromptTemplate/queryAll")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_insert_template(self, client: TestClient):
        """测试新增提示词模板"""
        response = client.post("/PromptTemplate/insert", json={
            "name": "新增测试模板",
            "test_type": "API",
            "template_type": "system",
            "content": "请生成{count}个测试用例",
            "is_active": True
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "id" in data["data"]
    
    def test_update_template(self, client: TestClient, session: Session):
        """测试更新提示词模板"""
        from aiassistant.model.PromptTemplate import PromptTemplate
        
        template = PromptTemplate(
            name="待更新模板",
            test_type="API",
            template_type="system",
            content="原始内容",
            is_active=True,
            create_time=datetime.now()
        )
        session.add(template)
        session.commit()
        session.refresh(template)
        
        response = client.put("/PromptTemplate/update", json={
            "id": template.id,
            "name": "更新后的模板名",
            "content": "更新后的内容"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_update_template_not_found(self, client: TestClient):
        """测试更新不存在的提示词模板"""
        response = client.put("/PromptTemplate/update", json={
            "id": 99999,
            "name": "测试"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
    
    def test_delete_template(self, client: TestClient, session: Session):
        """测试删除提示词模板"""
        from aiassistant.model.PromptTemplate import PromptTemplate
        
        template = PromptTemplate(
            name="待删除模板",
            test_type="API",
            template_type="system",
            content="测试内容",
            is_active=True,
            create_time=datetime.now()
        )
        session.add(template)
        session.commit()
        session.refresh(template)
        
        response = client.delete(f"/PromptTemplate/delete?id={template.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_delete_template_not_found(self, client: TestClient):
        """测试删除不存在的提示词模板"""
        response = client.delete("/PromptTemplate/delete?id=99999")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
    
    def test_toggle_active(self, client: TestClient, session: Session):
        """测试切换模板激活状态"""
        from aiassistant.model.PromptTemplate import PromptTemplate
        
        template = PromptTemplate(
            name="切换状态模板",
            test_type="API",
            template_type="system",
            content="测试内容",
            is_active=True,
            create_time=datetime.now()
        )
        session.add(template)
        session.commit()
        session.refresh(template)
        
        response = client.post(f"/PromptTemplate/toggleActive?id={template.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "停用" in data["msg"]
    
    def test_toggle_active_not_found(self, client: TestClient):
        """测试切换不存在模板的状态"""
        response = client.post("/PromptTemplate/toggleActive?id=99999")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
    
    def test_query_by_test_type(self, client: TestClient, session: Session):
        """测试按测试类型查询激活模板"""
        from aiassistant.model.PromptTemplate import PromptTemplate
        
        template = PromptTemplate(
            name="App测试模板",
            test_type="App",
            template_type="system",
            content="App测试内容",
            is_active=True,
            create_time=datetime.now()
        )
        session.add(template)
        session.commit()
        
        response = client.get("/PromptTemplate/queryByTestType?test_type=App")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
