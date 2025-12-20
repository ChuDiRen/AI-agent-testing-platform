"""
API数据库配置Service
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlmodel import Session, select
from core.logger import get_logger

from ..model.ApiDbBaseModel import ApiDbBase

logger = get_logger(__name__)


class ApiDbBaseService:
    """API数据库配置服务"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def query_by_page(self, page: int, page_size: int, project_id: Optional[int] = None,
                      connect_name: Optional[str] = None) -> tuple[List[ApiDbBase], int]:
        """分页查询数据库配置"""
        offset = (page - 1) * page_size
        statement = select(ApiDbBase)
        
        if project_id and project_id > 0:
            statement = statement.where(ApiDbBase.project_id == project_id)
        if connect_name:
            statement = statement.where(ApiDbBase.name.like(f'%{connect_name}%'))
        
        datas = self.session.exec(statement.limit(page_size).offset(offset)).all()
        
        count_statement = select(ApiDbBase)
        if project_id and project_id > 0:
            count_statement = count_statement.where(ApiDbBase.project_id == project_id)
        if connect_name:
            count_statement = count_statement.where(ApiDbBase.name.like(f'%{connect_name}%'))
        
        total = len(self.session.exec(count_statement).all())
        return list(datas), total
    
    def get_by_id(self, db_id: int) -> Optional[ApiDbBase]:
        """根据ID查询数据库配置"""
        return self.session.get(ApiDbBase, db_id)
    
    def create(self, project_id: int, name: str, ref_name: str, db_type: str,
               host: str, port: int, username: str, password: str, database: str,
               is_enabled: str = "1") -> Optional[ApiDbBase]:
        """新增数据库配置"""
        import json
        
        statement = select(ApiDbBase).where(ApiDbBase.ref_name == ref_name)
        existing = self.session.exec(statement).first()
        if existing:
            return None
        
        # 组合数据库连接信息为JSON字符串
        db_info = json.dumps({
            "host": host,
            "port": port,
            "username": username,
            "password": password,
            "database": database
        }, ensure_ascii=False)
        
        db_config = ApiDbBase(
            project_id=project_id,
            name=name,
            ref_name=ref_name,
            db_type=db_type,
            db_info=db_info,
            is_enabled=is_enabled,
            create_time=datetime.now()
        )
        self.session.add(db_config)
        self.session.commit()
        self.session.refresh(db_config)
        return db_config
    
    def update(self, db_id: int, update_data: Dict[str, Any]) -> Optional[ApiDbBase]:
        """更新数据库配置"""
        db_config = self.get_by_id(db_id)
        if not db_config:
            return None
        
        for key, value in update_data.items():
            if value is not None:
                setattr(db_config, key, value)
        
        self.session.commit()
        self.session.refresh(db_config)
        return db_config
    
    def delete(self, db_id: int) -> bool:
        """删除数据库配置"""
        db_config = self.get_by_id(db_id)
        if not db_config:
            return False
        
        self.session.delete(db_config)
        self.session.commit()
        return True
    
    def toggle_enabled(self, db_id: int, is_enabled: str) -> Optional[ApiDbBase]:
        """启用或禁用数据库配置"""
        db_config = self.get_by_id(db_id)
        if not db_config:
            return None
        
        db_config.is_enabled = is_enabled
        self.session.commit()
        self.session.refresh(db_config)
        return db_config
    
    def query_by_project(self, project_id: int) -> List[ApiDbBase]:
        """根据项目ID查询启用的数据库配置列表"""
        statement = select(ApiDbBase).where(
            ApiDbBase.project_id == project_id,
            ApiDbBase.is_enabled == "1"
        )
        return list(self.session.exec(statement).all())
