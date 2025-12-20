"""
Mock服务Service
提供Mock数据的CRUD、匹配规则、响应生成等功能
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlmodel import Session, select, and_, or_

from apitest.model.ApiMockModel import ApiMock


class ApiMockService:
    def __init__(self, session: Session):
        self.session = session
    
    def query_by_page(self, page: int, page_size: int, project_id: Optional[int] = None,
                     mock_name: Optional[str] = None, request_method: Optional[str] = None,
                     is_enabled: Optional[int] = None) -> tuple[List[ApiMock], int]:
        """分页查询Mock数据"""
        statement = select(ApiMock)
        
        # 条件筛选
        if project_id:
            statement = statement.where(ApiMock.project_id == project_id)
        if mock_name:
            statement = statement.where(ApiMock.mock_name.contains(mock_name))
        if request_method:
            statement = statement.where(ApiMock.request_method == request_method)
        if is_enabled is not None:
            statement = statement.where(ApiMock.is_enabled == is_enabled)
        
        # 排序
        statement = statement.order_by(ApiMock.update_time.desc(), ApiMock.id.desc())
        
        # 查询总数
        total_statement = select(ApiMock)
        if project_id:
            total_statement = total_statement.where(ApiMock.project_id == project_id)
        if mock_name:
            total_statement = total_statement.where(ApiMock.mock_name.contains(mock_name))
        if request_method:
            total_statement = total_statement.where(ApiMock.request_method == request_method)
        if is_enabled is not None:
            total_statement = total_statement.where(ApiMock.is_enabled == is_enabled)
        
        total = len(self.session.exec(total_statement).all())
        
        # 分页查询
        offset = (page - 1) * page_size
        datas = self.session.exec(statement.limit(page_size).offset(offset)).all()
        
        return datas, total
    
    def get_by_id(self, id: int) -> Optional[ApiMock]:
        """根据ID查询Mock数据"""
        return self.session.get(ApiMock, id)
    
    def create(self, **kwargs) -> ApiMock:
        """创建Mock数据"""
        data = ApiMock(
            **kwargs,
            create_time=datetime.now(),
            update_time=datetime.now()
        )
        self.session.add(data)
        self.session.commit()
        self.session.refresh(data)
        return data
    
    def update(self, id: int, update_data: Dict[str, Any]) -> bool:
        """更新Mock数据"""
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
        """删除Mock数据"""
        data = self.get_by_id(id)
        if not data:
            return False
        
        self.session.delete(data)
        self.session.commit()
        return True
    
    def query_by_project(self, project_id: int) -> List[ApiMock]:
        """查询项目的所有Mock数据"""
        statement = select(ApiMock).where(
            ApiMock.project_id == project_id
        ).order_by(ApiMock.update_time.desc(), ApiMock.id.desc())
        
        return self.session.exec(statement).all()
    
    def get_by_url_method(self, request_url: str, request_method: str, project_id: int) -> Optional[ApiMock]:
        """根据URL和方法获取Mock数据"""
        statement = select(ApiMock).where(
            and_(
                ApiMock.request_url == request_url,
                ApiMock.request_method == request_method,
                ApiMock.project_id == project_id,
                ApiMock.is_enabled == 1
            )
        ).order_by(ApiMock.update_time.desc()).limit(1)
        
        return self.session.exec(statement).first()
    
    def toggle_enabled(self, id: int) -> Optional[ApiMock]:
        """切换Mock启用状态"""
        data = self.get_by_id(id)
        if not data:
            return None
        
        data.is_enabled = 1 if data.is_enabled == 0 else 0
        data.update_time = datetime.now()
        
        self.session.add(data)
        self.session.commit()
        
        return data
    
    def search_by_url(self, url_pattern: str, project_id: Optional[int] = None) -> List[ApiMock]:
        """根据URL模式搜索Mock数据"""
        statement = select(ApiMock).where(
            ApiMock.request_url.contains(url_pattern)
        )
        
        if project_id:
            statement = statement.where(ApiMock.project_id == project_id)
        
        statement = statement.order_by(ApiMock.update_time.desc())
        
        return self.session.exec(statement).all()
