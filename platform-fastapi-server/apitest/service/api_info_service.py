"""
接口信息Service
提供接口的CRUD、搜索、统计等功能
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlmodel import Session, select, and_, or_

from apitest.model.ApiInfoModel import ApiInfo
from apitest.model.ApiFolderModel import ApiFolder


class InfoService:
    def __init__(self, session: Session):
        self.session = session
    
    def query_by_page(self, page: int, page_size: int, project_id: Optional[int] = None, 
                     folder_id: Optional[int] = None, api_name: Optional[str] = None,
                     request_method: Optional[str] = None) -> tuple[List[ApiInfo], int]:
        """分页查询接口信息"""
        statement = select(ApiInfo)
        
        # 条件筛选
        if project_id:
            statement = statement.where(ApiInfo.project_id == project_id)
        if folder_id is not None:
            statement = statement.where(ApiInfo.folder_id == folder_id)
        if api_name:
            statement = statement.where(ApiInfo.api_name.contains(api_name))
        if request_method:
            statement = statement.where(ApiInfo.request_method == request_method)
        
        # 排序
        statement = statement.order_by(ApiInfo.id.desc())
        
        # 查询总数
        total_statement = select(ApiInfo)
        if project_id:
            total_statement = total_statement.where(ApiInfo.project_id == project_id)
        if folder_id is not None:
            total_statement = total_statement.where(ApiInfo.folder_id == folder_id)
        if api_name:
            total_statement = total_statement.where(ApiInfo.api_name.contains(api_name))
        if request_method:
            total_statement = total_statement.where(ApiInfo.request_method == request_method)
        
        total = len(self.session.exec(total_statement).all())
        
        # 分页查询
        offset = (page - 1) * page_size
        datas = self.session.exec(statement.limit(page_size).offset(offset)).all()
        
        return datas, total
    
    def get_by_id(self, id: int) -> Optional[ApiInfo]:
        """根据ID查询接口信息"""
        return self.session.get(ApiInfo, id)
    
    def create(self, **kwargs) -> ApiInfo:
        """创建接口信息"""
        data = ApiInfo(
            **kwargs,
            create_time=datetime.now()
        )
        self.session.add(data)
        self.session.commit()
        self.session.refresh(data)
        return data
    
    def update(self, id: int, update_data: Dict[str, Any]) -> bool:
        """更新接口信息"""
        data = self.get_by_id(id)
        if not data:
            return False
        
        for key, value in update_data.items():
            if value is not None:
                setattr(data, key, value)
        self.session.add(data)
        self.session.commit()
        return True
    
    def delete(self, id: int) -> bool:
        """删除接口信息"""
        data = self.get_by_id(id)
        if not data:
            return False
        
        self.session.delete(data)
        self.session.commit()
        return True
    
    def query_by_project(self, project_id: int) -> List[ApiInfo]:
        """查询项目的所有接口"""
        statement = select(ApiInfo).where(
            ApiInfo.project_id == project_id
        ).order_by(ApiInfo.folder_id, ApiInfo.sort_order, ApiInfo.id)
        
        return self.session.exec(statement).all()
    
    def query_by_folder(self, folder_id: int) -> List[ApiInfo]:
        """查询指定目录下的接口"""
        statement = select(ApiInfo).where(
            ApiInfo.folder_id == folder_id
        ).order_by(ApiInfo.sort_order, ApiInfo.id)
        
        return self.session.exec(statement).all()
    
    def search(self, keyword: str, project_id: Optional[int] = None) -> List[ApiInfo]:
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
        
        return self.session.exec(statement).all()
    
    def batch_update_folder(self, api_ids: List[int], folder_id: int) -> int:
        """批量更新接口的目录"""
        if not api_ids:
            return 0
        
        updated_count = 0
        for api_id in api_ids:
            api = self.get_by_id(api_id)
            if api:
                api.folder_id = folder_id
                self.session.add(api)
                updated_count += 1
        
        if updated_count > 0:
            self.session.commit()
        
        return updated_count
    
    def find_by_url_method(self, project_id: int, url: str, method: str) -> Optional[ApiInfo]:
        """根据URL和请求方法查找接口"""
        statement = select(ApiInfo).where(
            and_(
                ApiInfo.project_id == project_id,
                ApiInfo.request_url == url,
                ApiInfo.request_method == method
            )
        )
        return self.session.exec(statement).first()
    
    def get_statistics(self, project_id: int) -> Dict[str, Any]:
        """获取接口统计信息"""
        # 总接口数
        total_statement = select(ApiInfo).where(ApiInfo.project_id == project_id)
        total_count = len(self.session.exec(total_statement).all())
        
        # 按方法统计
        method_stats = {}
        for method in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']:
            count = len(self.session.exec(
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
        folders = self.session.exec(
            select(ApiFolder).where(ApiFolder.project_id == project_id)
        ).all()
        
        for folder in folders:
            count = len(self.session.exec(
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
