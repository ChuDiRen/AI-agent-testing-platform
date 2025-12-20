"""
集合详情管理完整工作流E2E测试
测试场景：创建集合 -> 添加用例 -> 配置数据驱动 -> 调整顺序 -> 批量操作
"""
import pytest
from sqlmodel import Session
from apitest.service.api_project_service import ApiProjectService
from apitest.service.api_collection_info_service import ApiCollectionInfoService
from apitest.service.api_collection_detail_service import ApiCollectionDetailService


class TestCollectionDetailWorkflow:
    """集合详情管理工作流测试"""
    
    @pytest.fixture
    def project_service(self, db_session: Session):
        return ApiProjectService(db_session)
    
    @pytest.fixture
    def collection_service(self, db_session: Session):
        return ApiCollectionInfoService(db_session)
    
    @pytest.fixture
    def detail_service(self, db_session: Session):
        return ApiCollectionDetailService(db_session)
    
    def test_complete_detail_management_workflow(
        self,
        project_service: ApiProjectService,
        collection_service: ApiCollectionInfoService,
        detail_service: ApiCollectionDetailService
    ):
        """测试完整的集合详情管理工作流"""
        
        project = project_service.create(
            project_name="详情管理测试项目",
            project_desc="测试集合详情管理功能"
        )
        assert project is not None
        
        plan = collection_service.create(
            project_id=project.id,
            plan_name="详情管理测试计划",
            plan_desc="测试集合详情"
        )
        assert plan is not None
        
        detail1 = detail_service.create(
            collection_info_id=plan.id,
            case_info_id=1,
            run_order=1
        )
        assert detail1 is not None
        
        detail2 = detail_service.create(
            collection_info_id=plan.id,
            case_info_id=2,
            run_order=2
        )
        assert detail2 is not None
        
        detail3 = detail_service.create(
            collection_info_id=plan.id,
            case_info_id=3,
            run_order=3
        )
        assert detail3 is not None
        
        details = detail_service.query_by_collection_id(plan.id)
        assert len(details) == 3
        
        result = detail_service.batch_update_order([
            {"id": detail1.id, "run_order": 3},
            {"id": detail2.id, "run_order": 1},
            {"id": detail3.id, "run_order": 2}
        ])
        assert result is True
        
        updated_details = detail_service.query_by_collection_id(plan.id)
        order_map = {d.id: d.run_order for d in updated_details}
        assert order_map[detail1.id] == 3
        assert order_map[detail2.id] == 1
        assert order_map[detail3.id] == 2
        
        project_service.delete(project.id)
    
    def test_ddt_configuration_workflow(
        self,
        project_service: ApiProjectService,
        collection_service: ApiCollectionInfoService,
        detail_service: ApiCollectionDetailService
    ):
        """测试数据驱动配置工作流"""
        
        project = project_service.create(
            project_name="DDT配置测试项目",
            project_desc="测试数据驱动配置"
        )
        
        plan = collection_service.create(
            project_id=project.id,
            plan_name="DDT配置测试计划",
            plan_desc="测试DDT"
        )
        
        detail = detail_service.create(
            collection_info_id=plan.id,
            case_info_id=1,
            run_order=1,
            ddt_data=[
                {"desc": "数据集1", "username": "user1", "password": "pass1"},
                {"desc": "数据集2", "username": "user2", "password": "pass2"}
            ]
        )
        assert detail is not None
        assert detail.ddt_data is not None
        
        updated = detail_service.update(
            detail.id,
            {
                "ddt_data": [
                    {"desc": "更新数据1", "username": "updated1", "password": "newpass1"},
                    {"desc": "更新数据2", "username": "updated2", "password": "newpass2"},
                    {"desc": "新增数据3", "username": "new3", "password": "newpass3"}
                ]
            }
        )
        assert updated is not None
        
        try:
            template = detail_service.get_ddt_template(case_info_id=1)
            assert template is not None
            assert "template" in template
            assert "variables" in template
            assert isinstance(template["template"], list)
        except ValueError:
            pytest.skip("测试用例不存在")
        
        project_service.delete(project.id)
    
    def test_batch_operations_workflow(
        self,
        project_service: ApiProjectService,
        collection_service: ApiCollectionInfoService,
        detail_service: ApiCollectionDetailService
    ):
        """测试批量操作工作流"""
        
        project = project_service.create(
            project_name="批量操作测试项目",
            project_desc="测试批量添加和更新"
        )
        
        plan = collection_service.create(
            project_id=project.id,
            plan_name="批量操作测试计划",
            plan_desc="测试批量功能"
        )
        
        added_count = detail_service.batch_add_cases(
            collection_info_id=plan.id,
            case_ids=[1, 2, 3, 4, 5]
        )
        assert added_count == 5
        
        details = detail_service.query_by_collection_id(plan.id)
        assert len(details) == 5
        
        update_list = [
            {"id": details[0].id, "run_order": 5},
            {"id": details[1].id, "run_order": 4},
            {"id": details[2].id, "run_order": 3},
            {"id": details[3].id, "run_order": 2},
            {"id": details[4].id, "run_order": 1}
        ]
        result = detail_service.batch_update_order(update_list)
        assert result is True
        
        updated_details = detail_service.query_by_collection_id(plan.id)
        orders = [d.run_order for d in updated_details]
        assert sorted(orders) == [1, 2, 3, 4, 5]
        
        for detail in details[:2]:
            detail_service.delete(detail.id)
        
        remaining = detail_service.query_by_collection_id(plan.id)
        assert len(remaining) == 3
        
        project_service.delete(project.id)
