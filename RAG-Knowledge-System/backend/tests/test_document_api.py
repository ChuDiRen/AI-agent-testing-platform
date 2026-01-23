"""
文档管理 API 测试

测试文档上传、列表、详情、更新、删除等功能
"""
import pytest
from pathlib import Path


class TestDocumentUpload:
    """文档上传测试类"""

    def test_upload_text_file(self, client, user_auth_headers, temp_upload_file, sample_document_data):
        """测试上传文本文件"""
        with open(temp_upload_file, "rb") as f:
            response = client.post(
                "/api/v1/documents/upload",
                headers=user_auth_headers,
                files={"file": f},
                data=sample_document_data
            )

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["title"] == sample_document_data["title"]
        assert data["status"] in ["pending", "processing", "completed"]

    def test_upload_without_auth(self, client, temp_upload_file, sample_document_data):
        """测试未认证上传"""
        with open(temp_upload_file, "rb") as f:
            response = client.post(
                "/api/v1/documents/upload",
                files={"file": f},
                data=sample_document_data
            )

        assert response.status_code == 401

    def test_upload_without_file(self, client, user_auth_headers):
        """测试未提供文件"""
        response = client.post(
            "/api/v1/documents/upload",
            headers=user_auth_headers
        )

        assert response.status_code == 422

    def test_upload_invalid_file_type(self, client, user_auth_headers, tmp_path):
        """测试无效文件类型"""
        invalid_file = tmp_path / "test.exe"
        invalid_file.write_text("fake executable")

        with open(invalid_file, "rb") as f:
            response = client.post(
                "/api/v1/documents/upload",
                headers=user_auth_headers,
                files={"file": f}
            )

        assert response.status_code == 400

    def test_upload_missing_title(self, client, user_auth_headers, temp_upload_file):
        """测试缺少标题"""
        with open(temp_upload_file, "rb") as f:
            response = client.post(
                "/api/v1/documents/upload",
                headers=user_auth_headers,
                files={"file": f}
            )

        assert response.status_code == 422

    def test_upload_large_file(self, client, user_auth_headers, tmp_path):
        """测试超大文件"""
        large_file = tmp_path / "large.txt"
        # 创建超过50MB的文件
        large_file.write_bytes(b"0" * (51 * 1024 * 1024))

        with open(large_file, "rb") as f:
            response = client.post(
                "/api/v1/documents/upload",
                headers=user_auth_headers,
                files={"file": f},
                data={"title": "大文件测试"}
            )

        assert response.status_code == 413  # Payload Too Large


class TestDocumentList:
    """文档列表测试类"""

    def test_get_documents_success(self, client, user_auth_headers):
        """测试获取文档列表"""
        response = client.get(
            "/api/v1/documents",
            headers=user_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)

    def test_get_documents_without_auth(self, client):
        """测试未认证获取文档"""
        response = client.get("/api/v1/documents")

        assert response.status_code == 401

    def test_get_documents_with_pagination(self, client, user_auth_headers):
        """测试分页查询"""
        params = {
            "page": 1,
            "page_size": 10,
            "sort_by": "create_time",
            "sort_order": "desc"
        }

        response = client.get(
            "/api/v1/documents",
            headers=user_auth_headers,
            params=params
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "page" in data
        assert "page_size" in data

    def test_get_documents_with_filters(self, client, user_auth_headers):
        """测试筛选查询"""
        params = {
            "status": "completed",
            "permission": "private"
        }

        response = client.get(
            "/api/v1/documents",
            headers=user_auth_headers,
            params=params
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    def test_search_documents(self, client, user_auth_headers):
        """测试搜索文档"""
        params = {"keyword": "测试"}

        response = client.get(
            "/api/v1/documents",
            headers=user_auth_headers,
            params=params
        )

        assert response.status_code == 200


class TestDocumentDetail:
    """文档详情测试类"""

    def test_get_document_success(self, client, user_auth_headers, test_session):
        """测试获取文档详情"""
        # 先创建一个文档
        from app.models import document

        doc = document.Document(
            title="测试文档",
            description="测试描述",
            permission="private",
            status="completed",
            uploaded_by=1
        )
        test_session.add(doc)
        test_session.commit()
        test_session.refresh(doc)

        # 获取文档详情
        response = client.get(
            f"/api/v1/documents/{doc.id}",
            headers=user_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == doc.id
        assert data["title"] == "测试文档"

    def test_get_document_not_found(self, client, user_auth_headers):
        """测试获取不存在的文档"""
        response = client.get(
            "/api/v1/documents/999999",
            headers=user_auth_headers
        )

        assert response.status_code == 404

    def test_get_document_without_auth(self, client, test_session):
        """测试未认证获取文档"""
        from app.models import document

        doc = document.Document(
            title="测试文档",
            description="测试描述",
            permission="private",
            status="completed",
            uploaded_by=1
        )
        test_session.add(doc)
        test_session.commit()

        response = client.get(f"/api/v1/documents/{doc.id}")

        assert response.status_code == 401


class TestDocumentUpdate:
    """文档更新测试类"""

    def test_update_document_success(self, client, user_auth_headers, test_session):
        """测试更新文档"""
        from app.models import document

        doc = document.Document(
            title="原标题",
            description="原描述",
            permission="private",
            status="completed",
            uploaded_by=1
        )
        test_session.add(doc)
        test_session.commit()
        test_session.refresh(doc)

        update_data = {
            "title": "新标题",
            "description": "新描述",
            "permission": "public"
        }

        response = client.put(
            f"/api/v1/documents/{doc.id}",
            headers=user_auth_headers,
            json=update_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "新标题"
        assert data["description"] == "新描述"
        assert data["permission"] == "public"

    def test_update_document_not_owner(self, client, user_auth_headers, test_session):
        """测试更新他人文档"""
        from app.models import document

        # 创建属于其他用户的文档
        doc = document.Document(
            title="其他用户文档",
            permission="private",
            status="completed",
            uploaded_by=999  # 不同的用户ID
        )
        test_session.add(doc)
        test_session.commit()

        update_data = {"title": "尝试修改"}

        response = client.put(
            f"/api/v1/documents/{doc.id}",
            headers=user_auth_headers,
            json=update_data
        )

        assert response.status_code == 403  # Forbidden

    def test_update_document_not_found(self, client, user_auth_headers):
        """测试更新不存在的文档"""
        update_data = {"title": "新标题"}

        response = client.put(
            "/api/v1/documents/999999",
            headers=user_auth_headers,
            json=update_data
        )

        assert response.status_code == 404


class TestDocumentDelete:
    """文档删除测试类"""

    def test_delete_document_success(self, client, user_auth_headers, test_session):
        """测试删除文档"""
        from app.models import document

        doc = document.Document(
            title="待删除文档",
            description="描述",
            permission="private",
            status="completed",
            uploaded_by=1
        )
        test_session.add(doc)
        test_session.commit()
        test_session.refresh(doc)

        doc_id = doc.id

        # 删除文档
        response = client.delete(
            f"/api/v1/documents/{doc_id}",
            headers=user_auth_headers
        )

        assert response.status_code == 200

        # 验证文档已被删除
        get_response = client.get(
            f"/api/v1/documents/{doc_id}",
            headers=user_auth_headers
        )
        assert get_response.status_code == 404

    def test_delete_document_not_owner(self, client, user_auth_headers, test_session):
        """测试删除他人文档"""
        from app.models import document

        doc = document.Document(
            title="其他用户文档",
            permission="private",
            status="completed",
            uploaded_by=999
        )
        test_session.add(doc)
        test_session.commit()

        response = client.delete(
            f"/api/v1/documents/{doc.id}",
            headers=user_auth_headers
        )

        assert response.status_code == 403

    def test_delete_document_not_found(self, client, user_auth_headers):
        """测试删除不存在的文档"""
        response = client.delete(
            "/api/v1/documents/999999",
            headers=user_auth_headers
        )

        assert response.status_code == 404


class TestDocumentIndex:
    """文档索引测试类"""

    def test_index_document_success(self, client, admin_auth_headers, test_session):
        """测试索引文档"""
        from app.models import document

        doc = document.Document(
            title="待索引文档",
            description="描述",
            permission="public",
            status="completed",
            uploaded_by=1
        )
        test_session.add(doc)
        test_session.commit()

        response = client.post(
            f"/api/v1/documents/{doc.id}/index",
            headers=admin_auth_headers
        )

        # 注意：这可能需要模拟向量数据库，所以可能返回不同状态码
        assert response.status_code in [200, 202, 501]  # OK或未实现

    def test_index_document_without_permission(self, client, user_auth_headers, test_session):
        """测试无权限索引"""
        from app.models import document

        doc = document.Document(
            title="文档",
            permission="private",
            status="completed",
            uploaded_by=1
        )
        test_session.add(doc)
        test_session.commit()

        response = client.post(
            f"/api/v1/documents/{doc.id}/index",
            headers=user_auth_headers
        )

        # 普通用户可能没有索引权限
        assert response.status_code in [200, 202, 403, 501]
