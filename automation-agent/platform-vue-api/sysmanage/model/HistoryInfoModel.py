from app import database

class HistoryInfo(database.Model):
    __tablename__ = "t_history_Info"
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    project_id = database.Column(database.Integer, default=None, comment='项目ID')
    coll_id = database.Column(database.Integer, default=None, comment='测试集合ID')
    name = database.Column(database.String(255), default=None, comment='名称')
    status = database.Column(database.String(255), default=None, comment='状态')
    type = database.Column(database.String(255), default=None, comment='类型')
    #添加一个duration属性，int类型 长度255
    duration = database.Column(database.Integer, default=None, comment='测试用时')
    # 添加一个detail属性，varchar类型 长度255
    detail = database.Column(database.String(255), default=None, comment='测试数据文件夹名字')
    create_time = database.Column(database.DateTime, default=None, comment='创建时间')