"""
接口用例Service
提供用例的CRUD、批量操作、统计等功能
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlmodel import Session, select, and_, or_

from apitest.model.ApiInfoCaseModel import ApiInfoCase
from apitest.model.ApiInfoModel import ApiInfo


class InfoCaseService:
    def __init__(self, session: Session):
        self.session = session
    
    def query_by_page(self, page: int, page_size: int, project_id: Optional[int] = None,
                     api_id: Optional[int] = None, case_name: Optional[str] = None,
                     case_type: Optional[str] = None) -> tuple[List[ApiInfoCase], int]:
        """分页查询用例信息"""
        statement = select(ApiInfoCase)
        
        # 条件筛选
        if project_id:
            statement = statement.where(ApiInfoCase.project_id == project_id)
        if api_id:
            statement = statement.where(ApiInfoCase.api_id == api_id)
        if case_name:
            statement = statement.where(ApiInfoCase.case_name.contains(case_name))
        if case_type:
            statement = statement.where(ApiInfoCase.case_type == case_type)
        
        # 排序
        statement = statement.order_by(ApiInfoCase.id.desc())
        
        # 查询总数
        total_statement = select(ApiInfoCase)
        if project_id:
            total_statement = total_statement.where(ApiInfoCase.project_id == project_id)
        if api_id:
            total_statement = total_statement.where(ApiInfoCase.api_id == api_id)
        if case_name:
            total_statement = total_statement.where(ApiInfoCase.case_name.contains(case_name))
        if case_type:
            total_statement = total_statement.where(ApiInfoCase.case_type == case_type)
        
        total = len(self.session.exec(total_statement).all())
        
        # 分页查询
        offset = (page - 1) * page_size
        datas = self.session.exec(statement.limit(page_size).offset(offset)).all()
        
        return datas, total
    
    def get_by_id(self, id: int) -> Optional[ApiInfoCase]:
        """根据ID查询用例信息"""
        return self.session.get(ApiInfoCase, id)
    
    def create(self, **kwargs) -> ApiInfoCase:
        """创建用例信息"""
        data = ApiInfoCase(
            **kwargs,
            create_time=datetime.now(),
            update_time=datetime.now()
        )
        self.session.add(data)
        self.session.commit()
        self.session.refresh(data)
        return data
    
    def update(self, id: int, update_data: Dict[str, Any]) -> bool:
        """更新用例信息"""
        data = self.get_by_id(id)
        if not data:
            return False
        
        for key, value in update_data.items():
            if value is not None:
                setattr(data, key, value)
        data.update_time = datetime.now()
        
        self.session.add(data)
        self.session.commit()
        return True
    
    def delete(self, id: int) -> bool:
        """删除用例信息"""
        data = self.get_by_id(id)
        if not data:
            return False
        
        self.session.delete(data)
        self.session.commit()
        return True
    
    def query_by_api(self, api_id: int) -> List[ApiInfoCase]:
        """查询指定接口的所有用例"""
        statement = select(ApiInfoCase).where(
            ApiInfoCase.api_id == api_id
        ).order_by(ApiInfoCase.sort_order, ApiInfoCase.id)
        
        return self.session.exec(statement).all()
    
    def query_by_project(self, project_id: int) -> List[ApiInfoCase]:
        """查询项目的所有用例"""
        statement = select(ApiInfoCase).where(
            ApiInfoCase.project_id == project_id
        ).order_by(ApiInfoCase.id.desc())
        
        return self.session.exec(statement).all()
    
    def batch_create(self, cases_data: List[Dict[str, Any]]) -> List[ApiInfoCase]:
        """批量创建用例"""
        created_cases = []
        for case_data in cases_data:
            case = self.create(**case_data)
            created_cases.append(case)
        return created_cases
    
    def batch_update(self, case_updates: List[Dict[str, Any]]) -> int:
        """批量更新用例"""
        updated_count = 0
        for update_data in case_updates:
            case_id = update_data.get('id')
            if case_id:
                update_data.pop('id', None)  # 移除id字段
                if self.update(case_id, update_data):
                    updated_count += 1
        
        return updated_count
    
    def batch_delete(self, case_ids: List[int]) -> int:
        """批量删除用例"""
        deleted_count = 0
        for case_id in case_ids:
            if self.delete(case_id):
                deleted_count += 1
        
        return deleted_count
    
    def copy_case(self, case_id: int, new_name: str) -> Optional[ApiInfoCase]:
        """复制用例"""
        original_case = self.get_by_id(case_id)
        if not original_case:
            return None
        
        # 创建副本
        copy_data = original_case.model_dump()
        copy_data['case_name'] = new_name
        copy_data.pop('id', None)
        copy_data.pop('create_time', None)
        copy_data.pop('update_time', None)
        
        return self.create(**copy_data)
    
    def get_statistics(self, project_id: int) -> Dict[str, Any]:
        """获取用例统计信息"""
        # 总用例数
        total_statement = select(ApiInfoCase).where(ApiInfoCase.project_id == project_id)
        total_count = len(self.session.exec(total_statement).all())
        
        # 按类型统计
        type_stats = {}
        for case_type in ['normal', 'ddt', 'performance', 'security']:
            count = len(self.session.exec(
                select(ApiInfoCase).where(
                    and_(
                        ApiInfoCase.project_id == project_id,
                        ApiInfoCase.case_type == case_type
                    )
                )
            ).all())
            if count > 0:
                type_stats[case_type] = count
        
        # 按接口统计
        api_stats = []
        apis = self.session.exec(
            select(ApiInfo).where(ApiInfo.project_id == project_id)
        ).all()
        
        for api in apis:
            count = len(self.session.exec(
                select(ApiInfoCase).where(
                    and_(
                        ApiInfoCase.project_id == project_id,
                        ApiInfoCase.api_id == api.id
                    )
                )
            ).all())
            if count > 0:
                api_stats.append({
                    'api_id': api.id,
                    'api_name': api.api_name,
                    'case_count': count
                })
        
        return {
            'total_count': total_count,
            'type_stats': type_stats,
            'api_stats': api_stats
        }
