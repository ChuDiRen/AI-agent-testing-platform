from app import database


# 表： 关键字表，维护对应的关键字数据
class ApiKeyWord(database.Model):
    __tablename__ = "t_api_keyword"
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    name = database.Column(database.String(255), comment='关键字名称')
    keyword_desc = database.Column(database.String(255), comment='关键字描述')
    operation_type_id = database.Column(database.Integer, comment='操作类型ID')
    keyword_fun_name = database.Column(database.String(255), comment='方法名')
    keyword_value = database.Column(database.String(255), comment='方法体')
    is_enabled = database.Column(database.String(255), comment='是否启动')
    create_time = database.Column(database.DateTime)