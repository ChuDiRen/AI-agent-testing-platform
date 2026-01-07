"""
机器人配置Service
提供机器人配置的CRUD操作
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from sqlmodel import Session, select

from msgmanage.model.RobotConfigModel import RobotConfig


class RobotConfigService:
    def __init__(self, session: Session):
        self.session = session

    def query_all(self) -> List[RobotConfig]:
        """查询所有机器人配置"""
        statement = select(RobotConfig)
        return self.session.exec(statement).all()

    def query_by_page(
        self,
        page: int,
        page_size: int,
        robot_type: Optional[str] = None,
        robot_name: Optional[str] = None,
        is_enabled: Optional[bool] = None
    ) -> Tuple[List[RobotConfig], int]:
        """分页查询机器人配置"""
        offset = (page - 1) * page_size
        statement = select(RobotConfig)

        # 添加过滤条件
        if robot_type:
            statement = statement.where(RobotConfig.robot_type == robot_type)
        if robot_name:
            statement = statement.where(RobotConfig.robot_name.contains(robot_name))
        if is_enabled is not None:
            statement = statement.where(RobotConfig.is_enabled == is_enabled)

        # 查询总数
        count_statement = select(RobotConfig)
        if robot_type:
            count_statement = count_statement.where(RobotConfig.robot_type == robot_type)
        if robot_name:
            count_statement = count_statement.where(RobotConfig.robot_name.contains(robot_name))
        if is_enabled is not None:
            count_statement = count_statement.where(RobotConfig.is_enabled == is_enabled)

        total = len(self.session.exec(count_statement).all())

        # 分页查询
        statement = statement.limit(page_size).offset(offset)
        robots = self.session.exec(statement).all()

        return robots, total

    def get_by_id(self, robot_id: int) -> Optional[RobotConfig]:
        """根据ID查询机器人配置"""
        return self.session.get(RobotConfig, robot_id)

    def create(self, **kwargs) -> RobotConfig:
        """创建机器人配置"""
        data = RobotConfig(
            **kwargs,
            create_time=datetime.now()
        )
        self.session.add(data)
        self.session.commit()
        self.session.refresh(data)
        return data

    def update(self, robot_id: int, update_data: Dict[str, Any]) -> bool:
        """更新机器人配置"""
        robot = self.get_by_id(robot_id)
        if not robot:
            return False

        for key, value in update_data.items():
            if value is not None:
                setattr(robot, key, value)

        robot.update_time = datetime.now()
        self.session.commit()
        return True

    def delete(self, robot_id: int) -> bool:
        """删除机器人配置"""
        robot = self.get_by_id(robot_id)
        if not robot:
            return False

        self.session.delete(robot)
        self.session.commit()
        return True

    def update_test_time(self, robot_id: int) -> bool:
        """更新最后测试时间"""
        robot = self.get_by_id(robot_id)
        if not robot:
            return False

        robot.last_test_time = datetime.now()
        self.session.commit()
        return True
