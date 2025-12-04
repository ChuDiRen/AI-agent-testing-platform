"""
DeptController 部门管理模块单元测试
"""
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlmodel import Session


class TestDeptController:
    """部门控制器测试类"""
    
    def test_get_tree(self, client: TestClient, session: Session):
        """测试获取部门树"""
        from sysmanage.model.dept import Dept
        
        # 创建父部门
        parent_dept = Dept(
            dept_name="总公司",
            parent_id=0,
            order_num=1,
            create_time=datetime.now()
        )
        session.add(parent_dept)
        session.commit()
        session.refresh(parent_dept)
        
        # 创建子部门
        child_dept = Dept(
            dept_name="研发部",
            parent_id=parent_dept.id,
            order_num=1,
            create_time=datetime.now()
        )
        session.add(child_dept)
        session.commit()
        
        response = client.get("/dept/tree")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "data" in data
    
    def test_query_by_id(self, client: TestClient, session: Session):
        """测试根据ID查询部门"""
        from sysmanage.model.dept import Dept
        
        dept = Dept(
            dept_name="测试部门",
            parent_id=0,
            order_num=1,
            create_time=datetime.now()
        )
        session.add(dept)
        session.commit()
        session.refresh(dept)
        
        response = client.get(f"/dept/queryById?id={dept.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["dept_name"] == "测试部门"
    
    def test_query_by_id_not_found(self, client: TestClient):
        """测试查询不存在的部门"""
        response = client.get("/dept/queryById?id=99999")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
    
    def test_insert_dept(self, client: TestClient):
        """测试新增部门"""
        response = client.post("/dept/insert", json={
            "dept_name": "新增测试部门",
            "parent_id": 0,
            "order_num": 1
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_update_dept(self, client: TestClient, session: Session):
        """测试更新部门"""
        from sysmanage.model.dept import Dept
        
        dept = Dept(
            dept_name="待更新部门",
            parent_id=0,
            order_num=1,
            create_time=datetime.now()
        )
        session.add(dept)
        session.commit()
        session.refresh(dept)
        
        response = client.put("/dept/update", json={
            "id": dept.id,
            "dept_name": "更新后的部门名"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_update_dept_not_found(self, client: TestClient):
        """测试更新不存在的部门"""
        response = client.put("/dept/update", json={
            "id": 99999,
            "dept_name": "测试"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
    
    def test_delete_dept(self, client: TestClient, session: Session):
        """测试删除部门"""
        from sysmanage.model.dept import Dept
        
        dept = Dept(
            dept_name="待删除部门",
            parent_id=0,
            order_num=1,
            create_time=datetime.now()
        )
        session.add(dept)
        session.commit()
        session.refresh(dept)
        
        response = client.delete(f"/dept/delete?id={dept.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_delete_dept_with_children(self, client: TestClient, session: Session):
        """测试删除有子部门的部门"""
        from sysmanage.model.dept import Dept
        
        parent = Dept(
            dept_name="有子部门的父部门",
            parent_id=0,
            order_num=1,
            create_time=datetime.now()
        )
        session.add(parent)
        session.commit()
        session.refresh(parent)
        
        child = Dept(
            dept_name="子部门",
            parent_id=parent.id,
            order_num=1,
            create_time=datetime.now()
        )
        session.add(child)
        session.commit()
        
        response = client.delete(f"/dept/delete?id={parent.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
        assert "子部门" in data["msg"]
    
    def test_delete_dept_with_users(self, client: TestClient, session: Session):
        """测试删除有用户的部门"""
        from sysmanage.model.dept import Dept
        from sysmanage.model.user import User
        
        dept = Dept(
            dept_name="有用户的部门",
            parent_id=0,
            order_num=1,
            create_time=datetime.now()
        )
        session.add(dept)
        session.commit()
        session.refresh(dept)
        
        user = User(
            username="dept_user",
            password="test123",
            dept_id=dept.id,
            status="1",
            create_time=datetime.now()
        )
        session.add(user)
        session.commit()
        
        response = client.delete(f"/dept/delete?id={dept.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
        assert "用户" in data["msg"]
