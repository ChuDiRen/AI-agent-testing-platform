from app import database

class ApiInfo(database.Model):
    __tablename__ = "t_api_info"
    id = database.Column(database.Integer, primary_key=True, comment='接口用例编号', autoincrement=True)
    project_id = database.Column(database.Integer, comment='项目ID')
    api_name = database.Column(database.String(255), comment='接口名称')
    request_method = database.Column(database.String(255), comment='请求方法')
    request_url = database.Column(database.String(255), comment='请求地址')
    request_params = database.Column(database.String(255), comment='URL参数')
    request_headers = database.Column(database.Text(collation='utf8_general_ci'), comment='请求头')
    debug_vars = database.Column(database.Text(collation='utf8_general_ci'), comment='调试参数')
    request_form_datas = database.Column(database.String(255), comment='form-data')
    request_www_form_datas = database.Column(database.String(255),comment='www-form-data')
    requests_json_data = database.Column(database.String(255), comment='json数据')
    request_files = database.Column(database.String(255), comment='文件列表')
    create_time = database.Column(database.DateTime)