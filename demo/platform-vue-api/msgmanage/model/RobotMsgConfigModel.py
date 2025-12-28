from datetime import datetime
from app import database

class RobotMsgConfig(database.Model):
    __tablename__ = "t_robot_msg_config"

    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    coll_id = database.Column(database.Integer, default=None, comment='测试集合id')
    robot_id = database.Column(database.Integer, default=None, comment='机器人ID')
    robot_name= database.Column(database.String(255), default=None, comment='机器人名称')
    coll_type= database.Column(database.String(255), default=None, comment='集合类型')
    robot_type = database.Column(database.Integer, default=None, comment='机器人类型')
    is_enabled = database.Column(database.Integer, default=None, comment='是否启用')
    create_time = database.Column(database.DateTime, default=datetime.utcnow, comment='创建时间')