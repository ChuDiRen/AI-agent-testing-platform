"""
API 文档接口测试
测试 ApiDocController 的所有接口
"""
import pytest
import json


class TestApiDocController:
    """API 文档 Controller 测试"""
    
    def test_generate_doc_json_format(self, api_client, unique_name):
        """测试生成API文档 - JSON格式"""
        # 先创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"文档测试项目_{unique_name}",
            "project_desc": "用于测试文档生成"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 创建接口
        api_response = api_client.post("/ApiInfo/insert", json={
            "project_id": project_id,
            "api_name": f"测试接口_{unique_name}",
            "request_url": "/test/api",
            "request_method": "GET",
            "api_desc": "测试接口描述"
        })
        api_client.assert_success(api_response)
        
        # 生成JSON格式文档
        response = api_client.get("/ApiDoc/generate", params={
            "project_id": project_id,
            "format": "json"
        })
        data = api_client.assert_success(response)
        
        # 验证文档结构
        assert "project" in data["data"]
        assert "categories" in data["data"]
        assert "api_count" in data["data"]
        assert "generate_time" in data["data"]
        
        # 验证项目信息
        assert data["data"]["project"]["id"] == project_id
        assert data["data"]["project"]["name"] == f"文档测试项目_{unique_name}"
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_generate_doc_markdown_format(self, api_client, unique_name):
        """测试生成API文档 - Markdown格式"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"Markdown文档_{unique_name}",
            "project_desc": "Markdown测试"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 创建目录
        folder_response = api_client.post("/ApiFolder/insert", json={
            "project_id": project_id,
            "folder_name": f"测试目录_{unique_name}"
        })
        folder_data = api_client.assert_success(folder_response)
        folder_id = folder_data["data"]["id"]
        
        # 创建接口
        api_response = api_client.post("/ApiInfo/insert", json={
            "project_id": project_id,
            "folder_id": folder_id,
            "api_name": f"Markdown接口_{unique_name}",
            "request_url": "/test/markdown",
            "request_method": "POST",
            "api_desc": "Markdown测试接口"
        })
        api_client.assert_success(api_response)
        
        # 生成Markdown格式文档
        response = api_client.get("/ApiDoc/generate", params={
            "project_id": project_id,
            "format": "markdown"
        })
        
        # 验证响应
        assert response.status_code == 200
        assert response.headers.get("content-type") == "text/markdown; charset=utf-8"
        
        # 验证Markdown内容
        content = response.text
        assert f"Markdown文档_{unique_name}" in content
        assert "API文档" in content
        assert "目录" in content
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_generate_doc_html_format(self, api_client, unique_name):
        """测试生成API文档 - HTML格式"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"HTML文档_{unique_name}",
            "project_desc": "HTML测试"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 创建接口
        api_response = api_client.post("/ApiInfo/insert", json={
            "project_id": project_id,
            "api_name": f"HTML接口_{unique_name}",
            "request_url": "/test/html",
            "request_method": "GET"
        })
        api_client.assert_success(api_response)
        
        # 生成HTML格式文档
        response = api_client.get("/ApiDoc/generate", params={
            "project_id": project_id,
            "format": "html"
        })
        
        # 验证响应
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        
        # 验证HTML内容
        content = response.text
        assert "<!DOCTYPE html>" in content
        assert f"HTML文档_{unique_name}" in content
        assert "<html" in content
        assert "</html>" in content
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_generate_doc_with_empty_project(self, api_client, unique_name):
        """测试生成API文档 - 空项目"""
        # 创建空项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"空项目_{unique_name}",
            "project_desc": "没有接口的项目"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 生成文档
        response = api_client.get("/ApiDoc/generate", params={
            "project_id": project_id,
            "format": "json"
        })
        data = api_client.assert_success(response)
        
        # 验证空项目文档
        assert data["data"]["api_count"] == 0
        assert len(data["data"]["categories"]) == 0
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_generate_doc_nonexistent_project(self, api_client):
        """测试生成API文档 - 不存在的项目"""
        response = api_client.get("/ApiDoc/generate", params={
            "project_id": 999999,
            "format": "json"
        })
        
        # 应该返回错误
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert data.get("code") != 200 or "不存在" in data.get("msg", "")
    
    def test_preview_doc_success(self, api_client, unique_name):
        """测试预览API文档 - 成功"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"预览项目_{unique_name}",
            "project_desc": "预览测试"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 创建接口
        api_response = api_client.post("/ApiInfo/insert", json={
            "project_id": project_id,
            "api_name": f"预览接口_{unique_name}",
            "request_url": "/test/preview",
            "request_method": "GET",
            "request_params": json.dumps([
                {"key": "id", "type": "integer", "required": True, "description": "ID参数"}
            ]),
            "request_headers": json.dumps([
                {"key": "Authorization", "value": "Bearer token"}
            ])
        })
        api_client.assert_success(api_response)
        
        # 预览文档
        response = api_client.get("/ApiDoc/preview", params={
            "project_id": project_id
        })
        
        # 验证响应
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        
        # 验证HTML内容包含接口信息
        content = response.text
        assert f"预览项目_{unique_name}" in content
        assert f"预览接口_{unique_name}" in content
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_preview_doc_nonexistent_project(self, api_client):
        """测试预览API文档 - 不存在的项目"""
        response = api_client.get("/ApiDoc/preview", params={
            "project_id": 999999
        })
        
        # 应该返回404或错误页面
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            content = response.text
            assert "不存在" in content or "404" in content
    
    def test_export_doc_markdown(self, api_client, unique_name):
        """测试导出API文档 - Markdown格式"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"导出项目_{unique_name}",
            "project_desc": "导出测试"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 创建接口
        api_response = api_client.post("/ApiInfo/insert", json={
            "project_id": project_id,
            "api_name": f"导出接口_{unique_name}",
            "request_url": "/test/export",
            "request_method": "POST"
        })
        api_client.assert_success(api_response)
        
        # 导出Markdown文档
        response = api_client.get("/ApiDoc/export", params={
            "project_id": project_id,
            "format": "markdown"
        })
        data = api_client.assert_success(response)
        
        # 验证导出数据
        assert "content" in data["data"]
        assert "filename" in data["data"]
        assert f"导出项目_{unique_name}" in data["data"]["content"]
        assert ".md" in data["data"]["filename"]
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_export_doc_json(self, api_client, unique_name):
        """测试导出API文档 - JSON格式"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"JSON导出_{unique_name}",
            "project_desc": "JSON导出测试"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 导出JSON文档
        response = api_client.get("/ApiDoc/export", params={
            "project_id": project_id,
            "format": "json"
        })
        data = api_client.assert_success(response)
        
        # 验证JSON结构
        assert "project" in data["data"]
        assert "categories" in data["data"]
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_export_doc_openapi(self, api_client, unique_name):
        """测试导出API文档 - OpenAPI格式"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"OpenAPI导出_{unique_name}",
            "project_desc": "OpenAPI测试"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 创建接口
        api_response = api_client.post("/ApiInfo/insert", json={
            "project_id": project_id,
            "api_name": f"OpenAPI接口_{unique_name}",
            "request_url": "/api/openapi",
            "request_method": "GET",
            "request_params": json.dumps([
                {"key": "page", "type": "integer", "required": False, "description": "页码"}
            ])
        })
        api_client.assert_success(api_response)
        
        # 导出OpenAPI文档
        response = api_client.get("/ApiDoc/export", params={
            "project_id": project_id,
            "format": "openapi"
        })
        data = api_client.assert_success(response)
        
        # 验证OpenAPI 3.0结构
        openapi_doc = data["data"]
        assert openapi_doc["openapi"] == "3.0.0"
        assert "info" in openapi_doc
        assert "paths" in openapi_doc
        assert openapi_doc["info"]["title"] == f"OpenAPI导出_{unique_name}"
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_get_api_detail_success(self, api_client, unique_name):
        """测试获取接口详情文档 - 成功"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"详情项目_{unique_name}",
            "project_desc": "详情测试"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 创建接口（包含完整信息）
        api_response = api_client.post("/ApiInfo/insert", json={
            "project_id": project_id,
            "api_name": f"详情接口_{unique_name}",
            "request_url": "/api/detail",
            "request_method": "POST",
            "api_desc": "详细的接口描述",
            "request_params": json.dumps([
                {"key": "id", "type": "integer", "required": True, "description": "ID"},
                {"key": "name", "type": "string", "required": False, "description": "名称"}
            ]),
            "request_headers": json.dumps([
                {"key": "Content-Type", "value": "application/json"},
                {"key": "Authorization", "value": "Bearer token"}
            ]),
            "requests_json_data": '{"test": "data", "value": 123}'
        })
        api_data = api_client.assert_success(api_response)
        api_id = api_data["data"]["id"]
        
        # 获取接口详情
        response = api_client.get("/ApiDoc/getApiDetail", params={
            "api_id": api_id
        })
        data = api_client.assert_success(response)
        
        # 验证详情结构
        detail = data["data"]
        assert detail["id"] == api_id
        assert detail["name"] == f"详情接口_{unique_name}"
        assert detail["method"] == "POST"
        assert detail["url"] == "/api/detail"
        assert "params" in detail
        assert "headers" in detail
        assert "body" in detail
        
        # 验证参数
        assert len(detail["params"]) == 2
        assert detail["params"][0]["key"] == "id"
        
        # 验证请求头
        assert len(detail["headers"]) == 2
        
        # 验证请求体
        assert detail["body"] is not None
        assert detail["body_type"] == "json"
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_get_api_detail_nonexistent(self, api_client):
        """测试获取接口详情文档 - 不存在的接口"""
        response = api_client.get("/ApiDoc/getApiDetail", params={
            "api_id": 999999
        })
        
        # 应该返回错误
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert data.get("code") != 200 or "不存在" in data.get("msg", "")
    
    def test_get_api_detail_minimal_data(self, api_client, unique_name):
        """测试获取接口详情文档 - 最小数据"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"最小数据_{unique_name}",
            "project_desc": "最小数据测试"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 创建最小接口（只有必填字段）
        api_response = api_client.post("/ApiInfo/insert", json={
            "project_id": project_id,
            "api_name": f"最小接口_{unique_name}",
            "request_url": "/api/minimal",
            "request_method": "GET"
        })
        api_data = api_client.assert_success(api_response)
        api_id = api_data["data"]["id"]
        
        # 获取接口详情
        response = api_client.get("/ApiDoc/getApiDetail", params={
            "api_id": api_id
        })
        data = api_client.assert_success(response)
        
        # 验证最小数据结构
        detail = data["data"]
        assert detail["id"] == api_id
        assert detail["name"] == f"最小接口_{unique_name}"
        assert detail["method"] == "GET"
        assert detail["url"] == "/api/minimal"
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})


class TestApiDocControllerEdgeCases:
    """API 文档 Controller 边界情况测试"""
    
    def test_generate_doc_invalid_format(self, api_client, unique_name):
        """测试生成文档 - 无效格式"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"格式测试_{unique_name}",
            "project_desc": "格式测试"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 使用无效格式
        response = api_client.get("/ApiDoc/generate", params={
            "project_id": project_id,
            "format": "invalid_format"
        })
        
        # 应该返回默认格式（JSON）或错误
        assert response.status_code in [200, 400]
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_generate_doc_with_complex_data(self, api_client, unique_name):
        """测试生成文档 - 复杂数据结构"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"复杂数据_{unique_name}",
            "project_desc": "包含复杂数据的项目"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 创建多个目录
        folders = []
        for i in range(3):
            folder_response = api_client.post("/ApiFolder/insert", json={
                "project_id": project_id,
                "folder_name": f"目录{i}_{unique_name}",
                "sort_order": i
            })
            folder_data = api_client.assert_success(folder_response)
            folders.append(folder_data["data"]["id"])
        
        # 在每个目录下创建接口
        for i, folder_id in enumerate(folders):
            for j in range(2):
                api_client.post("/ApiInfo/insert", json={
                    "project_id": project_id,
                    "folder_id": folder_id,
                    "api_name": f"接口{i}-{j}_{unique_name}",
                    "request_url": f"/api/{i}/{j}",
                    "request_method": "GET"
                })
        
        # 生成文档
        response = api_client.get("/ApiDoc/generate", params={
            "project_id": project_id,
            "format": "json"
        })
        data = api_client.assert_success(response)
        
        # 验证复杂结构
        assert data["data"]["api_count"] == 6
        assert len(data["data"]["categories"]) == 3
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_export_doc_all_formats(self, api_client, unique_name):
        """测试导出文档 - 所有格式"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"全格式_{unique_name}",
            "project_desc": "测试所有格式"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 测试所有支持的格式
        formats = ["json", "markdown", "openapi"]
        for fmt in formats:
            response = api_client.get("/ApiDoc/export", params={
                "project_id": project_id,
                "format": fmt
            })
            data = api_client.assert_success(response)
            assert "data" in data
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
