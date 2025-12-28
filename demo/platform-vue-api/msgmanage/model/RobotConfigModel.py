from app import database

class RobotConfig(database.Model):
    __tablename__ = "t_robot_config"

    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    robot_name = database.Column(database.String(255), default=None, comment='机器人名称')
    robot_type = database.Column(database.String(255), default=None, comment='机器人类型（钉钉、飞书、企业微信）')
    webhook_url = database.Column(database.String(255), default=None, comment='Webhook URL')
    message_template = database.Column(database.String(255), default=None, comment='消息模板内容')
    keywords = database.Column(database.String(255), default=None, comment='关键词及其对应的参数（JSON 格式）')
    create_time = database.Column(database.DateTime, default=None, comment='创建时间')