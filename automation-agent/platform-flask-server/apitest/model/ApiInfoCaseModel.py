from app import database

# 表： 测试用例信息表，维护一个单独的CASE表
class ApiInfoCase(database.Model):
    __tablename__ = "t_api_info_case"
    id = database.Column(database.Integer, primary_key=True, comment='API用例编号', autoincrement=True)
    project_id = database.Column(database.Integer, comment='项目ID')
    module_id = database.Column(database.Integer, comment='模块ID')
    case_name = database.Column(database.String(255), comment='用例名称')
    case_desc = database.Column(database.String(255), comment='用例描述')
    param_data = database.Column(database.String(255), comment='调试变量')
    pre_request = database.Column(database.String(255), comment='执行前事件')
    post_request = database.Column(database.String(255), comment='执行后事件')
    debug_info = database.Column(database.String(255), comment='调试信息')
    create_time = database.Column(database.DateTime)