"""
目录管理完整工作流E2E测试
测试场景：创建项目 -> 创建目录结构 -> 移动目录 -> 排序 -> 删除
"""
import pytest
from sqlmodel import Session
from apitest.service.api_project_service import ApiProjectService
from apitest.service.api_folder_service import ApiFolderService


class TestFolderManagementWorkflow:
    """目录管理工作流测试"""
    
    @pytest.fixture
    def project_service(self, db_session: Session):
        return ApiProjectService(db_session)
    
    @pytest.fixture
    def folder_service(self, db_session: Session):
        return ApiFolderService(db_session)
    
    def test_complete_folder_hierarchy_workflow(
        self,
        project_service: ApiProjectService,
        folder_service: ApiFolderService
    ):
        """测试完整的目录层级管理工作流"""
        
        project = project_service.create(
            project_name="目录管理测试项目",
            project_desc="测试目录层级功能"
        )
        assert project is not None
        
        user_module = folder_service.create(
            project_id=project.id,
            folder_name="用户模块",
            parent_id=0,
            folder_desc="用户相关接口",
            sort_order=1
        )
        assert user_module is not None
        
        auth_folder = folder_service.create(
            project_id=project.id,
            folder_name="认证接口",
            parent_id=user_module.id,
            folder_desc="登录注册",
            sort_order=1
        )
        assert auth_folder is not None
        
        profile_folder = folder_service.create(
            project_id=project.id,
            folder_name="个人信息",
            parent_id=user_module.id,
            folder_desc="用户信息管理",
            sort_order=2
        )
        assert profile_folder is not None
        
        order_module = folder_service.create(
            project_id=project.id,
            folder_name="订单模块",
            parent_id=0,
            folder_desc="订单相关接口",
            sort_order=2
        )
        assert order_module is not None
        
        tree = folder_service.query_tree(project.id)
        assert len(tree) == 2
        assert tree[0]["folder_name"] == "用户模块"
        assert len(tree[0]["children"]) == 2
        
        moved = folder_service.move_folder(auth_folder.id, order_module.id)
        assert moved is not None
        assert moved.parent_id == order_module.id
        
        updated_tree = folder_service.query_tree(project.id)
        user_children = next(f for f in updated_tree if f["id"] == user_module.id)["children"]
        order_children = next(f for f in updated_tree if f["id"] == order_module.id)["children"]
        assert len(user_children) == 1
        assert len(order_children) == 1
        
        result = folder_service.batch_sort([
            {"id": user_module.id, "sort_order": 10},
            {"id": order_module.id, "sort_order": 5}
        ])
        assert result is True
        
        project_service.delete(project.id)
    
    def test_folder_move_validation_workflow(
        self,
        project_service: ApiProjectService,
        folder_service: ApiFolderService
    ):
        """测试目录移动验证工作流"""
        
        project = project_service.create(
            project_name="目录移动验证项目",
            project_desc="测试移动验证"
        )
        
        parent = folder_service.create(
            project_id=project.id,
            folder_name="父目录",
            parent_id=0
        )
        
        child = folder_service.create(
            project_id=project.id,
            folder_name="子目录",
            parent_id=parent.id
        )
        
        grandchild = folder_service.create(
            project_id=project.id,
            folder_name="孙目录",
            parent_id=child.id
        )
        
        result = folder_service.move_folder(parent.id, grandchild.id)
        assert result is None
        
        result = folder_service.move_folder(parent.id, child.id)
        assert result is None
        
        sibling = folder_service.create(
            project_id=project.id,
            folder_name="兄弟目录",
            parent_id=0
        )
        
        result = folder_service.move_folder(child.id, sibling.id)
        assert result is not None
        assert result.parent_id == sibling.id
        
        project_service.delete(project.id)
    
    def test_folder_deletion_workflow(
        self,
        project_service: ApiProjectService,
        folder_service: ApiFolderService
    ):
        """测试目录删除工作流"""
        
        project = project_service.create(
            project_name="目录删除测试项目",
            project_desc="测试删除功能"
        )
        
        parent = folder_service.create(
            project_id=project.id,
            folder_name="父目录",
            parent_id=0
        )
        
        child = folder_service.create(
            project_id=project.id,
            folder_name="子目录",
            parent_id=parent.id
        )
        
        result = folder_service.delete(parent.id)
        assert result is False
        
        result = folder_service.delete(child.id)
        assert result is True
        
        result = folder_service.delete(parent.id)
        assert result is True
        
        folders = folder_service.query_list(project.id)
        assert len(folders) == 0
        
        project_service.delete(project.id)
    
    def test_complex_folder_structure_workflow(
        self,
        project_service: ApiProjectService,
        folder_service: ApiFolderService
    ):
        """测试复杂目录结构工作流"""
        
        project = project_service.create(
            project_name="复杂目录结构项目",
            project_desc="测试复杂结构"
        )
        
        modules = {
            "用户模块": ["认证", "个人信息", "权限管理", "账号设置"],
            "订单模块": ["创建订单", "查询订单", "取消订单", "退款"],
            "商品模块": ["商品列表", "商品详情", "库存管理", "分类管理"],
            "支付模块": ["支付接口", "退款接口", "账单查询"]
        }
        
        created_folders = {}
        for module_name, subfolders in modules.items():
            parent = folder_service.create(
                project_id=project.id,
                folder_name=module_name,
                parent_id=0,
                sort_order=len(created_folders) + 1
            )
            created_folders[module_name] = {"parent": parent, "children": []}
            
            for idx, subfolder_name in enumerate(subfolders):
                child = folder_service.create(
                    project_id=project.id,
                    folder_name=subfolder_name,
                    parent_id=parent.id,
                    sort_order=idx + 1
                )
                created_folders[module_name]["children"].append(child)
        
        tree = folder_service.query_tree(project.id)
        assert len(tree) == 4
        
        total_children = sum(len(node["children"]) for node in tree)
        assert total_children == sum(len(subfolders) for subfolders in modules.values())
        
        all_folders = folder_service.query_list(project.id)
        assert len(all_folders) == 4 + sum(len(subfolders) for subfolders in modules.values())
        
        project_service.delete(project.id)
