from app import database

# 表： 操作类型表，比如：浏览器操作、元素操作...
class OperationType(database.Model):
    __tablename__ = "t_api_operationtype"
    id = database.Column(database.Integer, primary_key=True, autoincrement=True,comment='操作类型ID')
    operation_type_name = database.Column(database.String(255),comment= "操作类型名称")
    ex_fun_name = database.Column(database.String(255),comment= "操作类型方法名")
    create_time = database.Column(database.DateTime,comment= "创建时间")