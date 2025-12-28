from app import database

# 表：单个测试用例表
class ApiCollectionDetail(database.Model):
    __tablename__ = "t_api_collection_detail"
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    collection_info_id = database.Column(database.Integer,comment='测试集合ID')
    api_case_info_id = database.Column(database.Integer, comment='测试用例ID')
    ddt_param_data = database.Column(database.Text,comment='测试用例DDT数据')
    run_order = database.Column(database.Integer,comment='执行顺序')
    create_time = database.Column(database.DateTime)