"""
接口用例Service - 已重构为静态方法模式
提供用例的CRUD、批量操作、统计等功能
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from sqlmodel import Session, select, and_

from apitest.model.ApiInfoCaseModel import ApiInfoCase
from apitest.model.ApiInfoModel import ApiInfo
from apitest.schemas.ApiInfoCaseSchema import ApiInfoCaseQuery, ApiInfoCaseCreate, ApiInfoCaseUpdate


class InfoCaseService:
    """接口用例服务类 - 使用静态方法模式"""

    @staticmethod
    def query_by_page(session: Session, query: ApiInfoCaseQuery) -> Tuple[List[ApiInfoCase], int]:
        """分页查询用例信息"""
        offset = (query.page - 1) * query.pageSize
        statement = select(ApiInfoCase)

        # 应用过滤条件
        if query.project_id:
            statement = statement.where(ApiInfoCase.project_id == query.project_id)
        if hasattr(query, 'api_id') and query.api_id:
            statement = statement.where(ApiInfoCase.api_id == query.api_id)
        if query.case_name:
            statement = statement.where(ApiInfoCase.case_name.contains(query.case_name))

        # 排序
        statement = statement.order_by(ApiInfoCase.id.desc())
        statement = statement.limit(query.pageSize).offset(offset)
        datas = session.exec(statement).all()

        # 统计总数
        count_statement = select(ApiInfoCase)
        if query.project_id:
            count_statement = count_statement.where(ApiInfoCase.project_id == query.project_id)
        if hasattr(query, 'api_id') and query.api_id:
            count_statement = count_statement.where(ApiInfoCase.api_id == query.api_id)
        if query.case_name:
            count_statement = count_statement.where(ApiInfoCase.case_name.contains(query.case_name))
        total = len(session.exec(count_statement).all())

        return list(datas), total

    @staticmethod
    def query_by_id(session: Session, id: int) -> Optional[ApiInfoCase]:
        """根据ID查询用例信息"""
        return session.get(ApiInfoCase, id)

    @staticmethod
    def create(session: Session, case_data: ApiInfoCaseCreate) -> ApiInfoCase:
        """创建用例信息"""
        data = ApiInfoCase(
            **case_data.model_dump(),
            create_time=datetime.now(),
            update_time=datetime.now()
        )
        session.add(data)
        session.commit()
        session.refresh(data)
        return data

    @staticmethod
    def update(session: Session, case_data: ApiInfoCaseUpdate) -> Optional[ApiInfoCase]:
        """更新用例信息"""
        statement = select(ApiInfoCase).where(ApiInfoCase.id == case_data.id)
        db_case = session.exec(statement).first()
        if not db_case:
            return None

        update_data = case_data.model_dump(exclude_unset=True, exclude={'id'})
        for key, value in update_data.items():
            setattr(db_case, key, value)
        db_case.update_time = datetime.now()

        session.commit()
        return db_case

    @staticmethod
    def delete(session: Session, id: int) -> bool:
        """删除用例信息"""
        case = session.get(ApiInfoCase, id)
        if not case:
            return False

        session.delete(case)
        session.commit()
        return True

    @staticmethod
    def query_by_api(session: Session, api_id: int) -> List[ApiInfoCase]:
        """查询指定接口的所有用例"""
        statement = select(ApiInfoCase).where(
            ApiInfoCase.api_id == api_id
        ).order_by(ApiInfoCase.id)

        return list(session.exec(statement).all())

    @staticmethod
    def query_by_project(session: Session, project_id: int) -> List[ApiInfoCase]:
        """查询项目的所有用例"""
        statement = select(ApiInfoCase).where(
            ApiInfoCase.project_id == project_id
        ).order_by(ApiInfoCase.id.desc())

        return list(session.exec(statement).all())

    @staticmethod
    def batch_create(session: Session, cases_data: List[Dict[str, Any]]) -> List[ApiInfoCase]:
        """批量创建用例"""
        created_cases = []
        for case_data in cases_data:
            case = ApiInfoCase(
                **case_data,
                create_time=datetime.now(),
                update_time=datetime.now()
            )
            session.add(case)
            created_cases.append(case)

        session.commit()
        for case in created_cases:
            session.refresh(case)

        return created_cases

    @staticmethod
    def batch_update(session: Session, case_updates: List[Dict[str, Any]]) -> int:
        """批量更新用例"""
        updated_count = 0
        for update_data in case_updates:
            case_id = update_data.get('id')
            if case_id:
                case = session.get(ApiInfoCase, case_id)
                if case:
                    for key, value in update_data.items():
                        if key != 'id' and value is not None:
                            setattr(case, key, value)
                    case.update_time = datetime.now()
                    updated_count += 1

        if updated_count > 0:
            session.commit()

        return updated_count

    @staticmethod
    def batch_delete(session: Session, case_ids: List[int]) -> int:
        """批量删除用例"""
        deleted_count = 0
        for case_id in case_ids:
            case = session.get(ApiInfoCase, case_id)
            if case:
                session.delete(case)
                deleted_count += 1

        if deleted_count > 0:
            session.commit()

        return deleted_count

    @staticmethod
    def copy_case(session: Session, case_id: int, new_name: str) -> Optional[ApiInfoCase]:
        """复制用例"""
        original_case = session.get(ApiInfoCase, case_id)
        if not original_case:
            return None

        # 创建副本
        copy_data = original_case.model_dump()
        copy_data['case_name'] = new_name
        copy_data.pop('id', None)
        copy_data.pop('create_time', None)
        copy_data.pop('update_time', None)

        new_case = ApiInfoCase(
            **copy_data,
            create_time=datetime.now(),
            update_time=datetime.now()
        )
        session.add(new_case)
        session.commit()
        session.refresh(new_case)

        return new_case

    @staticmethod
    def get_statistics(session: Session, project_id: int) -> Dict[str, Any]:
        """获取用例统计信息"""
        # 总用例数
        total_statement = select(ApiInfoCase).where(ApiInfoCase.project_id == project_id)
        total_count = len(session.exec(total_statement).all())

        # 按接口统计
        api_stats = []
        apis = session.exec(
            select(ApiInfo).where(ApiInfo.project_id == project_id)
        ).all()

        for api in apis:
            count = len(session.exec(
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
            'api_stats': api_stats
        }
