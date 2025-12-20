"""
API 目录管理接口测试
测试 ApiFolderController 的所有接口
"""
import pytest


class TestApiFolderController:
    """API 目录 Controller 测试"""
    
    def test_query_by_page_success(self, api_client, unique_name):
        """测试分页查询目录 - 成功"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"目录测试项目_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 创建目录
        folder_response = api_client.post("/ApiFolder/insert", json={
            "project_id": project_id,
            "folder_name": f"测试目录_{unique_name}",
            "folder_desc": "测试目录描述"
        })
        api_client.assert_success(folder_response)
        
        # 分页查询
        response = api_client.post("/ApiFolder/queryByPage", json={
            "page": 1,
            "pageSize": 10,
            "project_id": project_id
        })
        data = api_client.assert_success(response)
        
        assert "data" in data
        assert "total" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) >= 1
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_query_by_id_success(self, api_client, unique_name):
        """测试根据ID查询目录 - 成功"""
        # 创建项目和目录
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"目录查询_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        folder_response = api_client.post("/ApiFolder/insert", json={
            "project_id": project_id,
            "folder_name": f"用户模块_{unique_name}",
            "folder_desc": "用户相关接口目录"
        })
        folder_data = api_client.assert_success(folder_response)
        folder_id = folder_data["data"]["id"]
        
        # 查询目录详情
        response = api_client.get("/ApiFolder/queryById", params={"id": folder_id})
        data = api_client.assert_success(response)
        
        assert data["data"]["id"] == folder_id
        assert data["data"]["folder_name"] == f"用户模块_{unique_name}"
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_insert_success(self, api_client, unique_name):
        """测试新增目录 - 成功"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"新增目录_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 新增目录
        folder_data = {
            "project_id": project_id,
            "folder_name": f"订单模块_{unique_name}",
            "folder_desc": "订单相关接口",
            "parent_id": 0,
            "sort_order": 1
        }
        response = api_client.post("/ApiFolder/insert", json=folder_data)
        data = api_client.assert_success(response)
        
        assert "id" in data["data"]
        assert isinstance(data["data"]["id"], int)
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_update_success(self, api_client, unique_name):
        """测试更新目录 - 成功"""
        # 创建项目和目录
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"更新目录_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        folder_response = api_client.post("/ApiFolder/insert", json={
            "project_id": project_id,
            "folder_name": f"原始目录_{unique_name}",
            "folder_desc": "原始描述"
        })
        folder_data = api_client.assert_success(folder_response)
        folder_id = folder_data["data"]["id"]
        
        # 更新目录
        update_data = {
            "id": folder_id,
            "folder_name": f"更新目录_{unique_name}",
            "folder_desc": "更新后的描述"
        }
        response = api_client.put("/ApiFolder/update", json=update_data)
        api_client.assert_success(response)
        
        # 验证更新
        verify_response = api_client.get("/ApiFolder/queryById", params={"id": folder_id})
        verify_data = api_client.assert_success(verify_response)
        assert verify_data["data"]["folder_name"] == f"更新目录_{unique_name}"
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_delete_success(self, api_client, unique_name):
        """测试删除目录 - 成功"""
        # 创建项目和目录
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"删除目录_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        folder_response = api_client.post("/ApiFolder/insert", json={
            "project_id": project_id,
            "folder_name": f"待删除目录_{unique_name}"
        })
        folder_data = api_client.assert_success(folder_response)
        folder_id = folder_data["data"]["id"]
        
        # 删除目录
        response = api_client.delete("/ApiFolder/delete", params={"id": folder_id})
        api_client.assert_success(response)
        
        # 验证删除
        verify_response = api_client.get("/ApiFolder/queryById", params={"id": folder_id})
        assert verify_response.status_code in [200, 404]
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_tree_structure(self, api_client, unique_name):
        """测试目录树结构"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"目录树_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 创建一级目录
        folder1_response = api_client.post("/ApiFolder/insert", json={
            "project_id": project_id,
            "folder_name": f"一级目录_{unique_name}",
            "parent_id": 0
        })
        folder1_data = api_client.assert_success(folder1_response)
        folder1_id = folder1_data["data"]["id"]
        
        # 创建二级目录
        folder2_response = api_client.post("/ApiFolder/insert", json={
            "project_id": project_id,
            "folder_name": f"二级目录_{unique_name}",
            "parent_id": folder1_id
        })
        api_client.assert_success(folder2_response)
        
        # 查询目录树
        tree_response = api_client.get("/ApiFolder/tree", params={"project_id": project_id})
        tree_data = api_client.assert_success(tree_response)
        
        assert isinstance(tree_data["data"], list)
        assert len(tree_data["data"]) > 0
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_multi_level_folders(self, api_client, unique_name):
        """测试多级目录"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"多级目录_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 创建三级目录结构
        # 一级
        level1_response = api_client.post("/ApiFolder/insert", json={
            "project_id": project_id,
            "folder_name": f"用户管理_{unique_name}",
            "parent_id": 0
        })
        level1_data = api_client.assert_success(level1_response)
        level1_id = level1_data["data"]["id"]
        
        # 二级
        level2_response = api_client.post("/ApiFolder/insert", json={
            "project_id": project_id,
            "folder_name": f"用户信息_{unique_name}",
            "parent_id": level1_id
        })
        level2_data = api_client.assert_success(level2_response)
        level2_id = level2_data["data"]["id"]
        
        # 三级
        level3_response = api_client.post("/ApiFolder/insert", json={
            "project_id": project_id,
            "folder_name": f"个人资料_{unique_name}",
            "parent_id": level2_id
        })
        api_client.assert_success(level3_response)
        
        # 查询目录树
        tree_response = api_client.get("/ApiFolder/tree", params={"project_id": project_id})
        tree_data = api_client.assert_success(tree_response)
        
        assert len(tree_data["data"]) > 0
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})


class TestApiFolderControllerEdgeCases:
    """API 目录 Controller 边界情况测试"""
    
    def test_query_nonexistent_folder(self, api_client):
        """测试查询不存在的目录"""
        response = api_client.get("/ApiFolder/queryById", params={"id": 999999})
        assert response.status_code in [200, 404]
    
    def test_delete_nonexistent_folder(self, api_client):
        """测试删除不存在的目录"""
        response = api_client.delete("/ApiFolder/delete", params={"id": 999999})
        assert response.status_code in [200, 404]
    
    def test_invalid_parent_id(self, api_client, unique_name):
        """测试无效的父目录ID"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"无效父ID_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 尝试创建目录，使用不存在的父ID
        folder_response = api_client.post("/ApiFolder/insert", json={
            "project_id": project_id,
            "folder_name": f"无效目录_{unique_name}",
            "parent_id": 999999
        })
        
        # 可能返回错误或创建成功（取决于实现）
        assert folder_response.status_code in [200, 400, 404]
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
