"""
文档生成完整 E2E 测试
测试 API 文档的生成、预览、导出等完整流程
"""
import pytest
import json


class TestDocumentGenerationE2E:
    """文档生成 E2E 测试"""
    
    def test_document_generation_workflow(self, api_client, unique_name):
        """测试文档生成完整工作流"""
        # 1. 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"文档项目_{unique_name}",
            "project_desc": "用于测试文档生成的项目"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        print(f"✓ 创建项目成功: ID={project_id}")
        
        # 2. 创建目录结构
        folder_response = api_client.post("/ApiFolder/insert", json={
            "project_id": project_id,
            "folder_name": f"用户模块_{unique_name}",
            "folder_desc": "用户相关接口"
        })
        folder_data = api_client.assert_success(folder_response)
        folder_id = folder_data["data"]["id"]
        
        # 3. 创建多个接口
        api_ids = []
        apis_data = [
            {
                "api_name": f"获取用户列表_{unique_name}",
                "request_url": "/api/users",
                "request_method": "GET",
                "api_desc": "获取所有用户列表",
                "request_params": json.dumps([
                    {"key": "page", "type": "integer", "required": False, "description": "页码"},
                    {"key": "size", "type": "integer", "required": False, "description": "每页数量"}
                ])
            },
            {
                "api_name": f"创建用户_{unique_name}",
                "request_url": "/api/users",
                "request_method": "POST",
                "api_desc": "创建新用户",
                "requests_json_data": json.dumps({
                    "username": "string",
                    "email": "string",
                    "password": "string"
                })
            },
            {
                "api_name": f"更新用户_{unique_name}",
                "request_url": "/api/users/{id}",
                "request_method": "PUT",
                "api_desc": "更新用户信息"
            },
            {
                "api_name": f"删除用户_{unique_name}",
                "request_url": "/api/users/{id}",
                "request_method": "DELETE",
                "api_desc": "删除指定用户"
            }
        ]
        
        for api_data in apis_data:
            api_data.update({
                "project_id": project_id,
                "folder_id": folder_id
            })
            response = api_client.post("/ApiInfo/insert", json=api_data)
            result = api_client.assert_success(response)
            api_ids.append(result["data"]["id"])
        
        print(f"✓ 创建了 {len(api_ids)} 个接口")
        
        # 4. 生成 JSON 格式文档
        json_doc_response = api_client.get("/ApiDoc/generate", params={
            "project_id": project_id,
            "format": "json"
        })
        json_doc_data = api_client.assert_success(json_doc_response)
        
        # 验证 JSON 文档结构
        assert "project" in json_doc_data["data"]
        assert "categories" in json_doc_data["data"]
        assert json_doc_data["data"]["api_count"] == 4
        print(f"✓ JSON 文档生成成功")
        
        # 5. 生成 Markdown 格式文档
        md_doc_response = api_client.get("/ApiDoc/generate", params={
            "project_id": project_id,
            "format": "markdown"
        })
        assert md_doc_response.status_code == 200
        md_content = md_doc_response.text
        assert f"文档项目_{unique_name}" in md_content
        print(f"✓ Markdown 文档生成成功")
        
        # 6. 生成 HTML 格式文档
        html_doc_response = api_client.get("/ApiDoc/generate", params={
            "project_id": project_id,
            "format": "html"
        })
        assert html_doc_response.status_code == 200
        html_content = html_doc_response.text
        assert "<!DOCTYPE html>" in html_content
        assert f"文档项目_{unique_name}" in html_content
        print(f"✓ HTML 文档生成成功")
        
        # 7. 预览文档
        preview_response = api_client.get("/ApiDoc/preview", params={
            "project_id": project_id
        })
        assert preview_response.status_code == 200
        print(f"✓ 文档预览成功")
        
        # 8. 导出 OpenAPI 格式
        openapi_response = api_client.get("/ApiDoc/export", params={
            "project_id": project_id,
            "format": "openapi"
        })
        openapi_data = api_client.assert_success(openapi_response)
        
        # 验证 OpenAPI 3.0 结构
        openapi_doc = openapi_data["data"]
        assert openapi_doc["openapi"] == "3.0.0"
        assert "info" in openapi_doc
        assert "paths" in openapi_doc
        assert openapi_doc["info"]["title"] == f"文档项目_{unique_name}"
        print(f"✓ OpenAPI 文档导出成功")
        
        # 9. 获取单个接口详情文档
        detail_response = api_client.get("/ApiDoc/getApiDetail", params={
            "api_id": api_ids[0]
        })
        detail_data = api_client.assert_success(detail_response)
        
        # 验证接口详情
        assert detail_data["data"]["name"] == f"获取用户列表_{unique_name}"
        assert detail_data["data"]["method"] == "GET"
        assert "params" in detail_data["data"]
        print(f"✓ 接口详情文档获取成功")
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
        print(f"✓ 测试清理完成")
    
    def test_document_with_complex_structure(self, api_client, unique_name):
        """测试复杂结构的文档生成"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"复杂文档_{unique_name}",
            "project_desc": "包含复杂结构的项目"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 创建多级目录
        folders = {}
        
        # 一级目录
        for module in ["用户模块", "订单模块", "商品模块"]:
            folder_response = api_client.post("/ApiFolder/insert", json={
                "project_id": project_id,
                "folder_name": f"{module}_{unique_name}",
                "parent_id": 0
            })
            folder_data = api_client.assert_success(folder_response)
            folders[module] = folder_data["data"]["id"]
            
            # 二级目录
            for sub in ["查询", "管理"]:
                sub_folder_response = api_client.post("/ApiFolder/insert", json={
                    "project_id": project_id,
                    "folder_name": f"{sub}_{unique_name}",
                    "parent_id": folder_data["data"]["id"]
                })
                sub_folder_data = api_client.assert_success(sub_folder_response)
                
                # 在每个二级目录下创建接口
                api_client.post("/ApiInfo/insert", json={
                    "project_id": project_id,
                    "folder_id": sub_folder_data["data"]["id"],
                    "api_name": f"{module}-{sub}接口_{unique_name}",
                    "request_url": f"/api/{module.lower()}/{sub.lower()}",
                    "request_method": "GET"
                })
        
        print(f"✓ 创建了复杂的目录和接口结构")
        
        # 生成文档
        doc_response = api_client.get("/ApiDoc/generate", params={
            "project_id": project_id,
            "format": "json"
        })
        doc_data = api_client.assert_success(doc_response)
        
        # 验证文档包含所有分类
        assert len(doc_data["data"]["categories"]) >= 3
        print(f"✓ 复杂结构文档生成成功")
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
    
    def test_document_export_all_formats(self, api_client, unique_name):
        """测试导出所有格式的文档"""
        # 创建项目和接口
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"导出测试_{unique_name}"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        api_client.post("/ApiInfo/insert", json={
            "project_id": project_id,
            "api_name": f"测试接口_{unique_name}",
            "request_url": "/api/test",
            "request_method": "GET"
        })
        
        # 测试所有导出格式
        formats = ["json", "markdown", "openapi"]
        for fmt in formats:
            export_response = api_client.get("/ApiDoc/export", params={
                "project_id": project_id,
                "format": fmt
            })
            
            if fmt == "json":
                export_data = api_client.assert_success(export_response)
                assert "project" in export_data["data"]
            elif fmt == "markdown":
                export_data = api_client.assert_success(export_response)
                assert "content" in export_data["data"]
                assert ".md" in export_data["data"]["filename"]
            elif fmt == "openapi":
                export_data = api_client.assert_success(export_response)
                assert export_data["data"]["openapi"] == "3.0.0"
            
            print(f"✓ {fmt.upper()} 格式导出成功")
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})


class TestDocumentWithMetadata:
    """带元数据的文档测试"""
    
    def test_document_with_metadata(self, api_client, unique_name):
        """测试包含元数据的文档"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"元数据文档_{unique_name}",
            "project_desc": "包含元数据的文档项目",
            "version": "1.0.0",
            "author": "测试团队"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 创建接口（包含详细信息）
        api_client.post("/ApiInfo/insert", json={
            "project_id": project_id,
            "api_name": f"详细接口_{unique_name}",
            "request_url": "/api/detailed",
            "request_method": "POST",
            "api_desc": "这是一个包含详细信息的接口",
            "request_params": json.dumps([
                {
                    "key": "id",
                    "type": "integer",
                    "required": True,
                    "description": "用户ID",
                    "example": 123
                }
            ]),
            "request_headers": json.dumps([
                {
                    "key": "Authorization",
                    "value": "Bearer {{token}}",
                    "description": "认证令牌"
                },
                {
                    "key": "Content-Type",
                    "value": "application/json"
                }
            ]),
            "requests_json_data": json.dumps({
                "name": "string",
                "age": "integer",
                "email": "string"
            }),
            "response_example": json.dumps({
                "code": 200,
                "msg": "success",
                "data": {
                    "id": 1,
                    "name": "测试用户"
                }
            })
        })
        
        # 生成包含元数据的文档
        doc_response = api_client.get("/ApiDoc/generate", params={
            "project_id": project_id,
            "format": "json"
        })
        doc_data = api_client.assert_success(doc_response)
        
        # 验证元数据
        assert doc_data["data"]["project"]["name"] == f"元数据文档_{unique_name}"
        print(f"✓ 元数据文档生成成功")
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})


class TestDocumentVersioning:
    """文档版本管理测试"""
    
    def test_document_versioning(self, api_client, unique_name):
        """测试文档版本管理"""
        # 创建项目
        project_response = api_client.post("/ApiProject/insert", json={
            "project_name": f"版本文档_{unique_name}",
            "version": "1.0.0"
        })
        project_data = api_client.assert_success(project_response)
        project_id = project_data["data"]["id"]
        
        # 创建 V1 接口
        api_v1_response = api_client.post("/ApiInfo/insert", json={
            "project_id": project_id,
            "api_name": f"接口V1_{unique_name}",
            "request_url": "/api/v1/resource",
            "request_method": "GET",
            "api_desc": "V1版本接口"
        })
        api_client.assert_success(api_v1_response)
        
        # 生成 V1 文档
        doc_v1_response = api_client.get("/ApiDoc/generate", params={
            "project_id": project_id,
            "format": "json"
        })
        doc_v1_data = api_client.assert_success(doc_v1_response)
        print(f"✓ V1 文档生成成功")
        
        # 更新项目版本
        api_client.put("/ApiProject/update", json={
            "id": project_id,
            "version": "2.0.0"
        })
        
        # 创建 V2 接口
        api_v2_response = api_client.post("/ApiInfo/insert", json={
            "project_id": project_id,
            "api_name": f"接口V2_{unique_name}",
            "request_url": "/api/v2/resource",
            "request_method": "GET",
            "api_desc": "V2版本接口"
        })
        api_client.assert_success(api_v2_response)
        
        # 生成 V2 文档
        doc_v2_response = api_client.get("/ApiDoc/generate", params={
            "project_id": project_id,
            "format": "json"
        })
        doc_v2_data = api_client.assert_success(doc_v2_response)
        
        # 验证版本差异
        assert doc_v2_data["data"]["api_count"] == 2
        print(f"✓ V2 文档生成成功，包含 2 个接口")
        
        # 清理
        api_client.delete("/ApiProject/delete", params={"id": project_id})
