"""
AiModelController AI模型管理模块单元测试
"""
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlmodel import Session


class TestAiModelController:
    """AI模型控制器测试类"""
    
    def test_query_by_page(self, client: TestClient, session: Session):
        """测试分页查询AI模型"""
        from aiassistant.model.AiModel import AiModel
        
        model = AiModel(
            model_name="测试模型",
            model_code="test_model",
            provider="openai",
            api_key="test_key",
            is_enabled=True,
            create_time=datetime.now()
        )
        session.add(model)
        session.commit()
        
        response = client.post("/AiModel/queryByPage", json={
            "page": 1,
            "pageSize": 10
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_query_by_page_with_filter(self, client: TestClient, session: Session):
        """测试带过滤的分页查询"""
        from aiassistant.model.AiModel import AiModel
        
        model = AiModel(
            model_name="DeepSeek模型",
            model_code="deepseek_model",
            provider="deepseek",
            api_key="test_key",
            is_enabled=True,
            create_time=datetime.now()
        )
        session.add(model)
        session.commit()
        
        response = client.post("/AiModel/queryByPage", json={
            "page": 1,
            "pageSize": 10,
            "provider": "deepseek"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_query_by_id(self, client: TestClient, session: Session):
        """测试根据ID查询AI模型"""
        from aiassistant.model.AiModel import AiModel
        
        model = AiModel(
            model_name="ID查询模型",
            model_code="id_query_model",
            provider="openai",
            api_key="test_key",
            is_enabled=True,
            create_time=datetime.now()
        )
        session.add(model)
        session.commit()
        session.refresh(model)
        
        response = client.get(f"/AiModel/queryById?id={model.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["model_name"] == "ID查询模型"
    
    def test_query_by_id_not_found(self, client: TestClient):
        """测试查询不存在的AI模型"""
        response = client.get("/AiModel/queryById?id=99999")
        
        assert response.status_code == 200
        data = response.json()
        assert "没有数据" in data.get("msg", "")
    
    def test_query_enabled(self, client: TestClient, session: Session):
        """测试查询所有启用的模型"""
        from aiassistant.model.AiModel import AiModel
        
        model = AiModel(
            model_name="启用的模型",
            model_code="enabled_model",
            provider="openai",
            api_key="test_key",
            is_enabled=True,
            create_time=datetime.now()
        )
        session.add(model)
        session.commit()
        
        response = client.get("/AiModel/queryEnabled")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_insert_model(self, client: TestClient):
        """测试新增AI模型"""
        response = client.post("/AiModel/insert", json={
            "model_name": "新增测试模型",
            "model_code": "new_test_model",
            "provider": "openai",
            "api_key": "sk-test-key",
            "api_url": "https://api.openai.com/v1",
            "is_enabled": True
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "id" in data["data"]
    
    def test_insert_duplicate_model(self, client: TestClient, session: Session):
        """测试新增重复模型代码"""
        from aiassistant.model.AiModel import AiModel
        
        model = AiModel(
            model_name="已存在模型",
            model_code="duplicate_model",
            provider="openai",
            api_key="test_key",
            is_enabled=True,
            create_time=datetime.now()
        )
        session.add(model)
        session.commit()
        
        response = client.post("/AiModel/insert", json={
            "model_name": "重复模型",
            "model_code": "duplicate_model",
            "provider": "openai",
            "api_key": "test_key"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
        assert "已存在" in data["msg"]
    
    def test_update_model(self, client: TestClient, session: Session):
        """测试更新AI模型"""
        from aiassistant.model.AiModel import AiModel
        
        model = AiModel(
            model_name="待更新模型",
            model_code="update_model",
            provider="openai",
            api_key="old_key",
            is_enabled=True,
            create_time=datetime.now()
        )
        session.add(model)
        session.commit()
        session.refresh(model)
        
        response = client.put("/AiModel/update", json={
            "id": model.id,
            "model_name": "更新后的模型名",
            "api_key": "new_key"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_update_model_not_found(self, client: TestClient):
        """测试更新不存在的AI模型"""
        response = client.put("/AiModel/update", json={
            "id": 99999,
            "model_name": "测试"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
    
    def test_delete_model(self, client: TestClient, session: Session):
        """测试删除AI模型"""
        from aiassistant.model.AiModel import AiModel
        
        model = AiModel(
            model_name="待删除模型",
            model_code="delete_model",
            provider="openai",
            api_key="test_key",
            is_enabled=True,
            create_time=datetime.now()
        )
        session.add(model)
        session.commit()
        session.refresh(model)
        
        response = client.delete(f"/AiModel/delete?id={model.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_delete_model_not_found(self, client: TestClient):
        """测试删除不存在的AI模型"""
        response = client.delete("/AiModel/delete?id=99999")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
    
    def test_toggle_status(self, client: TestClient, session: Session):
        """测试切换模型状态"""
        from aiassistant.model.AiModel import AiModel
        
        model = AiModel(
            model_name="切换状态模型",
            model_code="toggle_model",
            provider="openai",
            api_key="test_key",
            is_enabled=True,
            create_time=datetime.now()
        )
        session.add(model)
        session.commit()
        session.refresh(model)
        
        response = client.post(f"/AiModel/toggleStatus?id={model.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "禁用" in data["msg"]
    
    def test_toggle_status_not_found(self, client: TestClient):
        """测试切换不存在模型的状态"""
        response = client.post("/AiModel/toggleStatus?id=99999")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
