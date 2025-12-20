"""
环境管理Service
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlmodel import Session, select, and_
from core.logger import get_logger

from ..model.ApiEnvironmentModel import ApiEnvironment

logger = get_logger(__name__)


class ApiEnvironmentService:
    """环境管理服务"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def query_by_page(self, page: int, page_size: int, project_id: Optional[int] = None,
                      env_name: Optional[str] = None, env_code: Optional[str] = None,
                      is_enabled: Optional[int] = None) -> tuple[List[ApiEnvironment], int]:
        """分页查询环境列表"""
        offset = (page - 1) * page_size
        statement = select(ApiEnvironment)
        
        if project_id:
            statement = statement.where(ApiEnvironment.project_id == project_id)
        if env_name:
            statement = statement.where(ApiEnvironment.env_name.contains(env_name))
        if env_code:
            statement = statement.where(ApiEnvironment.env_code == env_code)
        if is_enabled is not None:
            statement = statement.where(ApiEnvironment.is_enabled == is_enabled)
        
        statement = statement.order_by(ApiEnvironment.sort_order, ApiEnvironment.id)
        
        total_statement = select(ApiEnvironment)
        if project_id:
            total_statement = total_statement.where(ApiEnvironment.project_id == project_id)
        total = len(self.session.exec(total_statement).all())
        
        datas = self.session.exec(statement.limit(page_size).offset(offset)).all()
        return list(datas), total
    
    def get_by_id(self, env_id: int) -> Optional[ApiEnvironment]:
        """根据ID查询环境"""
        return self.session.get(ApiEnvironment, env_id)
    
    def query_by_project(self, project_id: int) -> List[ApiEnvironment]:
        """查询项目下所有启用的环境"""
        statement = select(ApiEnvironment).where(
            and_(
                ApiEnvironment.project_id == project_id,
                ApiEnvironment.is_enabled == 1
            )
        ).order_by(ApiEnvironment.sort_order, ApiEnvironment.id)
        return list(self.session.exec(statement).all())
    
    def get_default_env(self, project_id: int) -> Optional[ApiEnvironment]:
        """获取项目的默认环境"""
        statement = select(ApiEnvironment).where(
            and_(
                ApiEnvironment.project_id == project_id,
                ApiEnvironment.is_default == 1,
                ApiEnvironment.is_enabled == 1
            )
        )
        env = self.session.exec(statement).first()
        
        if not env:
            statement = select(ApiEnvironment).where(
                and_(
                    ApiEnvironment.project_id == project_id,
                    ApiEnvironment.is_enabled == 1
                )
            ).order_by(ApiEnvironment.sort_order, ApiEnvironment.id)
            env = self.session.exec(statement).first()
        
        return env
    
    def create(self, project_id: int, env_name: str, env_code: str, base_url: str,
               env_desc: Optional[str] = None, is_default: int = 0, is_enabled: int = 1,
               sort_order: int = 0) -> ApiEnvironment:
        """新增环境"""
        env = ApiEnvironment(
            project_id=project_id,
            env_name=env_name,
            env_code=env_code,
            base_url=base_url,
            env_desc=env_desc,
            is_default=is_default,
            is_enabled=is_enabled,
            sort_order=sort_order,
            create_time=datetime.now()
        )
        self.session.add(env)
        self.session.commit()
        self.session.refresh(env)
        return env
    
    def update(self, env_id: int, update_data: Dict[str, Any]) -> Optional[ApiEnvironment]:
        """更新环境"""
        env = self.get_by_id(env_id)
        if not env:
            return None
        
        for key, value in update_data.items():
            if value is not None:
                setattr(env, key, value)
        
        self.session.commit()
        self.session.refresh(env)
        return env
    
    def delete(self, env_id: int) -> bool:
        """删除环境"""
        env = self.get_by_id(env_id)
        if not env:
            return False
        
        self.session.delete(env)
        self.session.commit()
        return True
    
    def set_default(self, env_id: int) -> Optional[ApiEnvironment]:
        """设置默认环境"""
        env = self.get_by_id(env_id)
        if not env:
            return None
        
        statement = select(ApiEnvironment).where(
            ApiEnvironment.project_id == env.project_id
        )
        all_envs = self.session.exec(statement).all()
        for e in all_envs:
            e.is_default = 0
        
        env.is_default = 1
        self.session.commit()
        self.session.refresh(env)
        return env
    
    def copy_environment(self, env_id: int, new_env_name: str, new_env_code: str) -> Optional[ApiEnvironment]:
        """复制环境"""
        original_env = self.get_by_id(env_id)
        if not original_env:
            return None
        
        new_env = ApiEnvironment(
            project_id=original_env.project_id,
            env_name=new_env_name,
            env_code=new_env_code,
            base_url=original_env.base_url,
            env_desc=original_env.env_desc,
            is_default=0,
            is_enabled=original_env.is_enabled,
            sort_order=original_env.sort_order,
            create_time=datetime.now()
        )
        self.session.add(new_env)
        self.session.commit()
        self.session.refresh(new_env)
        return new_env
