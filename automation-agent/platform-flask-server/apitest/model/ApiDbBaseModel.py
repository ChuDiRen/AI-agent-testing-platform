from app import database


# 表： 数据库信息表，维护对应的Web项目的数据库表
class ApiDbBase(database.Model):
    __tablename__ = "t_api_database"
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    project_id = database.Column(database.Integer, comment='项目ID')
    name = database.Column(database.String(255), comment='连接名')
    ref_name = database.Column(database.String(255), comment='引用变量')
    db_type = database.Column(database.String(255), comment='数据库类型')
    db_info = database.Column(database.String(255), comment='数据库连接信息')
    is_enabled = database.Column(database.String(255), comment='是否启用')
    create_time = database.Column(database.DateTime)