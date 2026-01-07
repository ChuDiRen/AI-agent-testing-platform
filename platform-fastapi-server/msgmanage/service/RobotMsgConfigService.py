"""
机器人消息模板配置Service
提供消息模板的CRUD操作
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from sqlmodel import Session, select

from msgmanage.model.RobotMsgConfigModel import RobotMsgConfig


class RobotMsgConfigService:
    def __init__(self, session: Session):
        self.session = session

    def query_by_page(
        self,
        page: int,
        page_size: int,
        robot_id: Optional[int] = None,
        msg_type: Optional[str] = None,
        template_name: Optional[str] = None,
        is_enabled: Optional[bool] = None
    ) -> Tuple[List[RobotMsgConfig], int]:
        """分页查询消息模板"""
        offset = (page - 1) * page_size
        statement = select(RobotMsgConfig)

        # 添加过滤条件
        if robot_id:
            statement = statement.where(RobotMsgConfig.robot_id == robot_id)
        if msg_type:
            statement = statement.where(RobotMsgConfig.msg_type == msg_type)
        if template_name:
            statement = statement.where(RobotMsgConfig.template_name.contains(template_name))
        if is_enabled is not None:
            statement = statement.where(RobotMsgConfig.is_enabled == is_enabled)

        # 查询总数
        count_statement = select(RobotMsgConfig)
        if robot_id:
            count_statement = count_statement.where(RobotMsgConfig.robot_id == robot_id)
        if msg_type:
            count_statement = count_statement.where(RobotMsgConfig.msg_type == msg_type)
        if template_name:
            count_statement = count_statement.where(RobotMsgConfig.template_name.contains(template_name))
        if is_enabled is not None:
            count_statement = count_statement.where(RobotMsgConfig.is_enabled == is_enabled)

        total = len(self.session.exec(count_statement).all())

        # 分页查询
        statement = statement.limit(page_size).offset(offset)
        templates = self.session.exec(statement).all()

        return templates, total

    def get_by_id(self, template_id: int) -> Optional[RobotMsgConfig]:
        """根据ID查询消息模板"""
        return self.session.get(RobotMsgConfig, template_id)

    def get_by_robot_id(self, robot_id: int) -> List[RobotMsgConfig]:
        """根据机器人ID查询所有启用的模板"""
        statement = select(RobotMsgConfig).where(
            RobotMsgConfig.robot_id == robot_id,
            RobotMsgConfig.is_enabled == True
        )
        return self.session.exec(statement).all()

    def create(self, **kwargs) -> RobotMsgConfig:
        """创建消息模板"""
        data = RobotMsgConfig(
            **kwargs,
            create_time=datetime.now()
        )
        self.session.add(data)
        self.session.commit()
        self.session.refresh(data)
        return data

    def update(self, template_id: int, update_data: Dict[str, Any]) -> bool:
        """更新消息模板"""
        template = self.get_by_id(template_id)
        if not template:
            return False

        for key, value in update_data.items():
            if value is not None:
                setattr(template, key, value)

        template.update_time = datetime.now()
        self.session.commit()
        return True

    def delete(self, template_id: int) -> bool:
        """删除消息模板"""
        template = self.get_by_id(template_id)
        if not template:
            return False

        self.session.delete(template)
        self.session.commit()
        return True
