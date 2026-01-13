from app import database


# 表：单个测试用例-操作步骤表
class ApiInfoCaseStep(database.Model):
    __tablename__ = "t_api_info_step"
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    api_case_info_id = database.Column(database.Integer, comment='用例的ID')
    key_word_id = database.Column(database.Integer, comment='关键字方法ID')
    step_desc = database.Column(database.String(255), comment='步骤描述')
    ref_variable = database.Column(database.String(255), comment='引用变量')
    run_order = database.Column(database.Integer, comment='步骤的顺序')
    create_time = database.Column(database.DateTime, comment='创建时间')
