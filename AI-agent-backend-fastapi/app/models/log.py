"""操作日志数据库模型"""
from sqlalchemy import Column, BigInteger, String, DateTime, Integer
from datetime import datetime
from app.core.database import Base


class OperationLog(Base):
    """操作日志表模型"""
    __tablename__ = "t_operation_log"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="日志ID")
    user_id = Column(BigInteger, nullable=True, comment="用户ID")
    username = Column(String(50), nullable=True, comment="用户名")
    action = Column(String(200), nullable=False, comment="操作动作")
    method = Column(String(10), nullable=False, comment="请求方法")
    path = Column(String(200), nullable=False, comment="请求路径")
    ip_address = Column(String(50), nullable=True, comment="IP地址")
    user_agent = Column(String(500), nullable=True, comment="用户代理")
    response_status = Column(Integer, nullable=True, comment="响应状态码")
    create_time = Column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
    
    def __repr__(self):
        return f"<OperationLog(id={self.id}, action={self.action}, user={self.username})>"
