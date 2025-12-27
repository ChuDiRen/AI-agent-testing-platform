"""
接口信息Service
提供接口的CRUD、搜索、统计等功能
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from sqlmodel import Session, select, and_, or_

from apitest.model.ApiInfoModel import ApiInfo
from apitest.model.ApiFolderModel import ApiFolder
from apitest.schemas.ApiInfoSchema import ApiInfoQuery, ApiInfoCreate, ApiInfoUpdate


class InfoService:
    """接口信息Service层 - 使用静态方法模式"""
    
    @staticmethod
    def query_by_page(session: Session, query: ApiInfoQuery) -> tuple[List[ApiInfo], int]:
        """分页查询接口信息"""
        offset = (query.page - 1) * query.pageSize
        statement = select(ApiInfo)
        
        # 应用过滤条件
        if query.project_id:
            statement = statement.where(ApiInfo.project_id == query.project_id)
        if query.folder_id is not None:
            statement = statement.where(ApiInfo.folder_id == query.folder_id)
        if query.api_name:
            statement = statement.where(ApiInfo.api_name.contains(query.api_name))
        if query.request_method:
            statement = statement.where(ApiInfo.request_method == query.request_method)
        
        statement = statement.limit(query.pageSize).offset(offset)
        datas = session.exec(statement).all()
        
        # 统计总数
        count_statement = select(ApiInfo)
        if query.project_id:
            count_statement = count_statement.where(ApiInfo.project_id == query.project_id)
        if query.folder_id is not None:
            count_statement = count_statement.where(ApiInfo.folder_id == query.folder_id)
        if query.api_name:
            count_statement = count_statement.where(ApiInfo.api_name.contains(query.api_name))
        if query.request_method:
            count_statement = count_statement.where(ApiInfo.request_method == query.request_method)
        
        total = len(session.exec(count_statement).all())
        
        return datas, total
    
    @staticmethod
    def query_by_id(session: Session, id: int) -> Optional[ApiInfo]:
        """根据ID查询接口信息"""
        return session.get(ApiInfo, id)
    
    @staticmethod
    def create(session: Session, api_info: ApiInfoCreate) -> ApiInfo:
        """创建接口信息"""
        data = ApiInfo(**api_info.model_dump(), create_time=datetime.now())
        session.add(data)
        session.commit()
        session.refresh(data)
        return data
    
    @staticmethod
    def update(session: Session, api_info: ApiInfoUpdate) -> bool:
        """更新接口信息"""
        data = session.get(ApiInfo, api_info.id)
        if not data:
            return False
        
        update_data = api_info.model_dump(exclude_unset=True, exclude={'id'})
        for key, value in update_data.items():
            if value is not None:
                setattr(data, key, value)
        session.add(data)
        session.commit()
        return True
    
    @staticmethod
    def delete(session: Session, id: int) -> bool:
        """删除接口信息"""
        data = session.get(ApiInfo, id)
        if not data:
            return False
        
        session.delete(data)
        session.commit()
        return True
    
    @staticmethod
    def query_by_project(session: Session, project_id: int) -> List[ApiInfo]:
        """查询项目的所有接口"""
        statement = select(ApiInfo).where(
            ApiInfo.project_id == project_id
        ).order_by(ApiInfo.folder_id, ApiInfo.sort_order, ApiInfo.id)
        
        return session.exec(statement).all()
    
    @staticmethod
    def query_by_folder(session: Session, folder_id: int) -> List[ApiInfo]:
        """查询指定目录下的接口"""
        statement = select(ApiInfo).where(
            ApiInfo.folder_id == folder_id
        ).order_by(ApiInfo.sort_order, ApiInfo.id)
        
        return session.exec(statement).all()
    
    @staticmethod
    def search(session: Session, keyword: str, project_id: Optional[int] = None) -> List[ApiInfo]:
        """搜索接口"""
        statement = select(ApiInfo).where(
            or_(
                ApiInfo.api_name.contains(keyword),
                ApiInfo.api_desc.contains(keyword),
                ApiInfo.request_url.contains(keyword)
            )
        )
        
        if project_id:
            statement = statement.where(ApiInfo.project_id == project_id)
        
        statement = statement.order_by(ApiInfo.id.desc())
        
        return session.exec(statement).all()
    
    @staticmethod
    def batch_update_folder(session: Session, api_ids: List[int], folder_id: int) -> int:
        """批量更新接口的目录"""
        if not api_ids:
            return 0
        
        updated_count = 0
        for api_id in api_ids:
            api = session.get(ApiInfo, api_id)
            if api:
                api.folder_id = folder_id
                session.add(api)
                updated_count += 1
        
        if updated_count > 0:
            session.commit()
        
        return updated_count
    
    @staticmethod
    def find_by_url_method(session: Session, project_id: int, url: str, method: str) -> Optional[ApiInfo]:
        """根据URL和请求方法查找接口"""
        statement = select(ApiInfo).where(
            and_(
                ApiInfo.project_id == project_id,
                ApiInfo.request_url == url,
                ApiInfo.request_method == method
            )
        )
        return session.exec(statement).first()
    
    @staticmethod
    def get_statistics(session: Session, project_id: int) -> Dict[str, Any]:
        """获取接口统计信息"""
        # 总接口数
        total_statement = select(ApiInfo).where(ApiInfo.project_id == project_id)
        total_count = len(session.exec(total_statement).all())

        # 按方法统计
        method_stats = {}
        for method in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']:
            count = len(session.exec(
                select(ApiInfo).where(
                    and_(
                        ApiInfo.project_id == project_id,
                        ApiInfo.request_method == method
                    )
                )
            ).all())
            if count > 0:
                method_stats[method] = count

        # 按目录统计
        folder_stats = []
        folders = session.exec(
            select(ApiFolder).where(ApiFolder.project_id == project_id)
        ).all()

        for folder in folders:
            count = len(session.exec(
                select(ApiInfo).where(
                    and_(
                        ApiInfo.project_id == project_id,
                        ApiInfo.folder_id == folder.id
                    )
                )
            ).all())
            folder_stats.append({
                'folder_id': folder.id,
                'folder_name': folder.folder_name,
                'count': count
            })

        return {
            'total_count': total_count,
            'method_stats': method_stats,
            'folder_stats': folder_stats
        }
