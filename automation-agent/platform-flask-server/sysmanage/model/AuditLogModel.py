from app import database
from datetime import datetime


class AuditLog(database.Model):
    __tablename__ = "t_audit_log"
    __table_args__ = {'extend_existing': True}

    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    user_id = database.Column(database.Integer, nullable=False, comment='用户ID')
    username = database.Column(database.String(64), default='', comment='用户名称')
    module = database.Column(database.String(64), default='', comment='功能模块')
    summary = database.Column(database.String(128), default='', comment='请求描述')
    method = database.Column(database.String(10), default='', comment='请求方法')
    path = database.Column(database.String(255), default='', comment='请求路径')
    status = database.Column(database.Integer, default=-1, comment='状态码')
    response_time = database.Column(database.Integer, default=0, comment='响应时间(单位ms)')
    request_args = database.Column(database.JSON, comment='请求参数')
    response_body = database.Column(database.JSON, comment='返回数据')
    created_at = database.Column(database.DateTime, default=datetime.now, comment='创建时间')
    updated_at = database.Column(database.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
